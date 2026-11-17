import Link from "next/link";
import { 
  FaFilePdf, 
  FaLayerGroup, 
  FaScissors, 
  FaCompress, 
  FaImage, 
  FaFolder, 
  FaArrowRight 
} from "@/components/ui/icons";

export default function HomePage() {
  const tools = [
    {
      slug: "merge-pdf",
      name: "Merge PDF",
      description: "Combine multiple PDF documents into a single ordered file with bookmark retention.",
      icon: FaLayerGroup,
      badge: "PDF-001",
    },
    {
      slug: "split-pdf",
      name: "Split PDF",
      description: "Extract specific page intervals or burst each page into an independent PDF file.",
      icon: FaScissors,
      badge: "PDF-002",
    },
    {
      slug: "compress-pdf",
      name: "Compress PDF",
      description: "Downsample image streams and recompress internal dictionaries for guaranteed size reduction.",
      icon: FaCompress,
      badge: "PDF-003",
    },
    {
      slug: "image-to-favicon",
      name: "Image to Favicon & Manifest",
      description: "Generate complete favicon suites (ICO, 16x16, 32x32, 180x180, 192x192, 512x512, site.webmanifest, and HTML tags).",
      icon: FaImage,
      badge: "WEB-DEV",
    },
    {
      slug: "jpg-to-pdf",
      name: "JPG to PDF",
      description: "Transform JPG, PNG, and WebP images into a standardized multi-page PDF document.",
      icon: FaImage,
      badge: "PDF-016",
    },
    {
      slug: "pdf-to-jpg",
      name: "PDF to JPG",
      description: "Render high-resolution raster images from PDF pages at selectable DPI densities.",
      icon: FaFilePdf,
      badge: "PDF-015",
    },
  ];

  return (
    <div className="space-y-16 py-12 sm:py-20">
      {/* Hero Section */}
      <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="border-4 border-black bg-white p-8 sm:p-14 shadow-flat">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
            {/* Left Content */}
            <div className="lg:col-span-7 space-y-6">
              <div className="inline-block bg-black text-white px-3 py-1 text-xs font-mono font-black uppercase tracking-widest">
                DOCUMENT STUDIO • 440 TOOLS • 20 CATEGORIES
              </div>

              <h1 className="text-4xl sm:text-6xl font-black uppercase tracking-tight text-black leading-none">
                All Your Document Tools In One Place.
              </h1>

              <p className="text-sm sm:text-base text-neutral-800 font-medium max-w-xl leading-relaxed">
                Fast, private, and effortless. Merge, split, compress, convert, edit, and organize all your documents and PDFs directly in your browser with zero quality loss.
              </p>

              <div className="flex flex-wrap items-center gap-4 pt-2">
                <Link
                  href="/tools"
                  className="inline-flex items-center gap-3 border-2 border-black bg-major-red px-6 py-3.5 text-xs font-black uppercase tracking-widest text-white shadow-flat hover:bg-black transition-colors"
                >
                  <span>Browse All 440 Tools</span>
                  <FaArrowRight className="h-3.5 w-3.5" />
                </Link>

                <Link
                  href="/tools/image-to-favicon"
                  className="inline-flex items-center gap-3 border-2 border-black bg-white px-6 py-3.5 text-xs font-black uppercase tracking-widest text-black hover:bg-neutral-100 transition-colors shadow-flat"
                >
                  <span>Favicon Studio</span>
                </Link>
              </div>
            </div>

            {/* Right Graphic: Stylized PDF Document Card matching user sketch */}
            <div className="lg:col-span-5 flex justify-center lg:justify-end">
              <div className="relative w-full max-w-[300px] sm:max-w-[330px]">
                {/* Back tilted document shadow layer */}
                <div className="absolute inset-0 translate-x-3 translate-y-3 border-4 border-black bg-neutral-200"></div>

                {/* Front White Document Sheet */}
                <div className="relative border-4 border-black bg-white p-7 shadow-flat flex flex-col justify-between min-h-[350px]">
                  {/* Top Header with Corner Badge */}
                  <div className="flex items-start justify-between">
                    <div className="h-3.5 w-3.5 bg-black"></div>
                    <div className="bg-major-red text-white text-[11px] font-mono font-black px-3 py-1 uppercase tracking-wider">
                      ORIGINAL DOC
                    </div>
                  </div>

                  {/* Big Bold PDF Stamp */}
                  <div className="my-6">
                    <div className="text-7xl sm:text-8xl font-black font-mono tracking-tighter text-major-red leading-none select-none">
                      PDF
                    </div>
                    <div className="mt-1 text-xs font-mono font-black uppercase tracking-widest text-black">
                      PORTABLE DOCUMENT
                    </div>
                  </div>

                  {/* Stylized Document Text Wireframe Lines */}
                  <div className="space-y-2.5 my-2">
                    <div className="h-2 bg-black w-full"></div>
                    <div className="h-2 bg-neutral-800 w-11/12"></div>
                    <div className="h-2 bg-neutral-400 w-4/5"></div>
                    <div className="h-2 bg-neutral-300 w-2/3"></div>
                  </div>

                  {/* Bottom Footer Info */}
                  <div className="mt-4 pt-4 border-t-2 border-black flex items-center justify-between text-[10px] font-mono font-bold uppercase text-black">
                    <span className="flex items-center gap-1.5">
                      <span className="h-2 w-2 bg-major-red inline-block"></span>
                      100% QUALITY
                    </span>
                    <span className="border border-black px-2 py-0.5 bg-neutral-100">
                      STUDIO READY
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Core Tools Section */}
      <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="border-b-2 border-black pb-4 mb-8 flex items-baseline justify-between">
          <div>
            <h2 className="text-2xl font-black uppercase tracking-tight text-black sm:text-3xl">
              Popular Tools
            </h2>
            <p className="mt-1 text-xs font-mono uppercase text-neutral-600">
              Most frequently used document tools and converters
            </p>
          </div>

          <Link
            href="/tools"
            className="text-xs font-black uppercase tracking-wider text-black hover:text-major-red flex items-center gap-1.5"
          >
            <span>View All</span>
            <FaArrowRight className="h-3 w-3" />
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {tools.map((tool) => {
            const Icon = tool.icon;
            return (
              <Link
                key={tool.slug}
                href={`/tools/${tool.slug}`}
                className="group flex flex-col justify-between border-2 border-black bg-white p-7 shadow-flat hover:border-major-red hover:shadow-flatHover transition-all"
              >
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex h-12 w-12 items-center justify-center bg-black text-white group-hover:bg-major-red transition-colors">
                      <Icon className="h-6 w-6" />
                    </div>
                    <span className="border border-black bg-neutral-100 px-2 py-0.5 text-[10px] font-mono font-bold uppercase text-black">
                      {tool.badge}
                    </span>
                  </div>

                  <h3 className="text-lg font-black uppercase tracking-tight text-black group-hover:text-major-red transition-colors">
                    {tool.name}
                  </h3>
                  <p className="mt-2 text-xs text-neutral-700 font-medium leading-relaxed">
                    {tool.description}
                  </p>
                </div>

                <div className="mt-8 pt-4 border-t-2 border-neutral-100 flex items-center justify-between text-xs font-black uppercase tracking-wider text-black">
                  <span>Open Tool</span>
                  <FaArrowRight className="h-3.5 w-3.5 group-hover:translate-x-1 transition-transform" />
                </div>
              </Link>
            );
          })}

          {/* Cloud Workspace Card */}
          <Link
            href="/workspace"
            className="group flex flex-col justify-between border-2 border-black bg-neutral-100 p-7 shadow-flat hover:bg-white hover:border-major-blue transition-all"
          >
            <div>
              <div className="flex items-center justify-between mb-6">
                <div className="flex h-12 w-12 items-center justify-center bg-black text-white group-hover:bg-major-blue transition-colors">
                  <FaFolder className="h-6 w-6" />
                </div>
                <span className="border border-black bg-white px-2 py-0.5 text-[10px] font-mono font-bold uppercase text-black">
                  STORAGE
                </span>
              </div>

              <h3 className="text-lg font-black uppercase tracking-tight text-black group-hover:text-major-blue transition-colors">
                Cloud Workspace
              </h3>
              <p className="mt-2 text-xs text-neutral-700 font-medium leading-relaxed">
                Persistent personal document storage with folder hierarchies, versioning, and secure public sharing links.
              </p>
            </div>

            <div className="mt-8 pt-4 border-t-2 border-neutral-200 flex items-center justify-between text-xs font-black uppercase tracking-wider text-black">
              <span>Open Workspace</span>
              <FaArrowRight className="h-3.5 w-3.5 group-hover:translate-x-1 transition-transform" />
            </div>
          </Link>
        </div>
      </section>

      {/* Platform Productivity Highlights */}
      <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="border-4 border-black bg-white p-8 sm:p-12 shadow-flat">
          <div className="border-b-2 border-black pb-6 mb-8 flex flex-col sm:flex-row sm:items-end justify-between gap-4">
            <div>
              <span className="text-xs font-mono uppercase tracking-widest text-major-red font-bold">
                DESIGNED FOR EVERYDAY PRODUCTIVITY
              </span>
              <h2 className="mt-2 text-2xl sm:text-3xl font-black uppercase tracking-tight text-black">
                Why Use PDF Pride
              </h2>
            </div>
            <p className="text-xs font-mono uppercase text-neutral-600">
              Clean • Private • 0% Quality Loss
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            <div className="border-2 border-black bg-neutral-50 p-6 shadow-flat">
              <span className="text-xs font-mono font-black text-major-red">01 / FAST PROCESSING</span>
              <h4 className="mt-2 text-base font-black uppercase text-black">Zero Wait Times</h4>
              <p className="mt-2 text-xs text-neutral-700 font-medium leading-relaxed">
                Run single or multi-file operations at lightning speed with instant download links the moment they finish.
              </p>
            </div>

            <div className="border-2 border-black bg-neutral-50 p-6 shadow-flat">
              <span className="text-xs font-mono font-black text-major-red">02 / FORMAT FIDELITY</span>
              <h4 className="mt-2 text-base font-black uppercase text-black">Real Office & Vector Files</h4>
              <p className="mt-2 text-xs text-neutral-700 font-medium leading-relaxed">
                PDF to Excel produces genuine editable spreadsheets; PDF to Word produces clean documents without broken layouts.
              </p>
            </div>

            <div className="border-2 border-black bg-neutral-50 p-6 shadow-flat">
              <span className="text-xs font-mono font-black text-major-red">03 / COMPLETE PRIVACY</span>
              <h4 className="mt-2 text-base font-black uppercase text-black">Your Data Stays Yours</h4>
              <p className="mt-2 text-xs text-neutral-700 font-medium leading-relaxed">
                All processed documents are handled in private sessions and cleaned up automatically after your download.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
