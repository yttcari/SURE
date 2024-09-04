using VIDA
using CairoMakie
using InteractiveUtils
using Plots
using OptimizationBBO
using CSV
using DataFrames
using HDF5

# Load Image
# img = load_image("avg_SgrA/SgrA_a+0.94_i30_f230.e9.h5")
# img = load_image(joinpath(dirname(pathof(VIDA)),"../example/data/example_image.fits"));
function load_im_h5(fname::String; polarization=false)
    img = h5open("5000.h5", "r") do fid
        println("debug1")
        header = fid["header"]
        dsource = read(header["dsource"])
        jyscale = read(header["scale"])
        rf = read(header["freqcgs"])
        tunit = read(header["units"]["T_unit"])
        lunit = read(header["units"]["L_unit"])
        dx = read(header["camera"]["dx"])
        nx = Int(read(header["camera"]["nx"]))
        time = read(header["t"])*tunit/3600
        temp = h5open(fname, "r") do file
            if polarization
                stokesI = collect(fid["pol"][1,:,:]')[end:-1:1,:]
                stokesQ = collect(fid["pol"][2,:,:]')[end:-1:1,:]
                stokesU = collect(fid["pol"][3,:,:]')[end:-1:1,:]
                stokesV = collect(fid["pol"][4,:,:]')[end:-1:1,:]
                image = StructArray{StokesParams{eltype(stokesI)}}((I=stokesI, Q=stokesQ, U=stokesU, V=stokesV))
            else
                println("debug")
                image = collect(file["data"][1,:,:]')[end:-1:1,:] 
            end
        end
        println("debug3")
        # Now convert everything to IntensityMap
        image = image.*jyscale
        src = "Unknown"
        ra = 0.0
        dec = 0.0

        # convert to μas
        fov = μas2rad(dx/dsource*lunit*2.06265e11)

        mjd = 53005
        ComradeBase.MinimalHeader(src, ra, dec, mjd, rf)
        g = imagepixels(fov, fov, nx, nx)

        return IntensityMap(image, g)
    end
    return img
end

function fitmring(fname::String, avg=false)  
    if avg
        image = load_im_h5(fname)
    else
        image = load_image(fname)
    end
    bh = Bhattacharyya(image);
    kl = KullbackLeibler(image);
    println("image loaded")
    # Extracting Optimal Template
    cos_temp(θ) = EllipticalSlashedGaussianRing(θ.r0, θ.σ, θ.τ, θ.ξτ, θ.s, θ.ξs, θ.x0, θ.y0) + θ.f*θ.f*VLBISkyModels.Constant(μas2rad(100.0))
    lower = (r0 = μas2rad(39.0),  σ = μas2rad(9), τ=0.0, ξτ=-π/2, s=0.04, ξs=-1π, x0 = μas2rad(-60.0), y0 = μas2rad(-60.0), f=1e-6)
    upper = (r0 = μas2rad(84.0), σ = μas2rad(21.0), τ=0.5, ξτ=π/2, s=0.48, ξs=1π, x0 = μas2rad(60.0), y0 = μas2rad(60.0), f=10.0)

    prob = VIDAProblem(bh, cos_temp, lower, upper);
    println("Start optimizing")
    xopt, optfilt, divmin = vida(prob, BBO_de_rand_1_bin_radiuslimited(); maxiters=50_000);

    @show divergence(bh, optfilt)

    # Viz
    println("Start visualization")
    axis=(xreversed=true, aspect=DataAspect())
    scale_length=fieldofview(image).X/4
    colormap=:afmhot
    if true
        fig = Figure(size=(750, 300))
        ax1 = Axis(fig[1,1]; axis...)
        ax2 = Axis(fig[1,2]; axis...)
        ax3 = Axis(fig[1,3], aspect=1, yticklabelsvisible=false)
        hidedecorations!.((ax1, ax2))

        #Construct the image grid in μas
        g = axisdims(image)

        Xitr = map(rad2μas, g.X)
        Yitr = map(rad2μas, g.Y)
        fovx, fovy = map(rad2μas, values(fieldofview(image)))

        gμas = RectiGrid((;X=Xitr, Y=Yitr);)
        dataim = IntensityMap(baseimage(image./flux(image)), gμas)
        println("viz1")
        #Construct the template image
        template_img = intensitymap(optfilt, g)
        fimg = IntensityMap(baseimage(template_img/flux(template_img)), gμas)

        #Get scale bar and slice data.
        size = 40#μas
        startx = fovx/2*(1-0.1)
        starty = -fovy/2*(1-0.2)
        xseg = range(startx, startx-size, length=4)
        yseg = starty*ones(4)
        #Finally the slices
        xx = collect(Xitr)
        yy = collect(Yitr)
        xcol,ycol = centroid(template_img)
        imin = argmin(abs.(xx .- xcol))
        jmin = argmin(abs.(yy .- ycol))
        println("viz2")
        color = Makie.to_colormap(colormap)[end]

        Makie.heatmap!(ax1, dataim, colormap=colormap)
        hlines!(ax1, [ycol], color=:cornflowerblue, linewidth=2, linestyle=:solid)
        vlines!(ax1, [xcol], color=:red, linewidth=2, linestyle=:solid)

        Makie.heatmap!(ax2, fimg, colormap=colormap)
        hlines!(ax2, [ycol], color=:cornflowerblue, linewidth=2, linestyle=:dash)
        vlines!(ax2, [xcol], color=:red, linewidth=2, linestyle=:dash)
        ax2.yticklabelsvisible = false

        lines!(ax3, reverse(Xitr), parent(dataim)[jmin, :], color=:cornflowerblue)
        lines!(ax3, Yitr, parent(dataim)[:, imin], color=:red)
        ax3.yaxisposition = :right
        ax3.ylabel = "Profile"
        lines!(ax3, reverse(Xitr), parent(fimg)[jmin, :], color=:cornflowerblue, linestyle=:dash)
        lines!(ax3, Yitr, parent(fimg)[:, imin], color=:red, linestyle=:dash)
        ax3.xlabel = "RA, DEC chords (μas)"
        colgap!(fig.layout, 5.0)
        colgap!(fig.layout, 2, 20.0)

    return fig, xopt
    end
end



# Output xopt to CSV
# function struct2df(s, filter, img)
#    field_names = fieldnames(typeof(s))
#    field_values = [getfield(s, f) for f in field_names]
#    
#    data = Dict(field_names .=> field_values)
#    data[:div] = divergence(bh, filter)
#    df = DataFrame(data)
#    
#    return df
# end
#
# df = struct2df(xopt, optfilt, img)
# CSV.write("output.csv", df, append=true, header=true)
