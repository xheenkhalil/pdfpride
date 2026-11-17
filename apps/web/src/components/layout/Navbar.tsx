import Link from "next/link";
import { FaFilePdf, FaLayerGroup, FaFolder } from "@/components/ui/icons";

export function Navbar() {
  return (
    <header className="sticky top-0 z-50 w-full border-b-2 border-black bg-white">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-8">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="flex h-10 w-10 items-center justify-center bg-major-red text-white">
              <FaFilePdf className="h-5 w-5" />
            </div>
            <div className="flex flex-col">
              <span className="text-xl font-black tracking-tight uppercase text-black font-mono">
                PDF<span className="text-major-red">PRIDE</span>
              </span>
              <span className="text-[10px] font-bold text-black tracking-widest uppercase">
                Document Studio
              </span>
            </div>
          </Link>

          <nav className="hidden md:flex items-center gap-6 text-xs font-bold uppercase tracking-wider text-black">
            <Link href="/tools" className="hover:text-major-red transition-colors flex items-center gap-1.5 py-1 border-b-2 border-transparent hover:border-major-red">
              <FaLayerGroup className="h-3.5 w-3.5 text-black" />
              All Tools
            </Link>
            <Link href="/tools/merge-pdf" className="hover:text-major-red transition-colors py-1 border-b-2 border-transparent hover:border-major-red">
              Merge
            </Link>
            <Link href="/tools/split-pdf" className="hover:text-major-red transition-colors py-1 border-b-2 border-transparent hover:border-major-red">
              Split
            </Link>
            <Link href="/tools/compress-pdf" className="hover:text-major-red transition-colors py-1 border-b-2 border-transparent hover:border-major-red">
              Compress
            </Link>
            <Link href="/tools/image-to-favicon" className="hover:text-major-blue text-major-blue transition-colors py-1 border-b-2 border-transparent hover:border-major-blue">
              Favicon Studio
            </Link>
            <Link href="/tools/jpg-to-pdf" className="hover:text-major-red transition-colors py-1 border-b-2 border-transparent hover:border-major-red">
              Convert
            </Link>
          </nav>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/workspace"
            className="hidden sm:inline-flex items-center gap-2 border-2 border-black bg-white px-4 py-2 text-xs font-bold uppercase tracking-wider text-black hover:bg-neutral-100 transition-colors"
          >
            <FaFolder className="h-3.5 w-3.5 text-black" />
            Workspace
          </Link>

          <Link
            href="/tools"
            className="inline-flex items-center gap-2 border-2 border-black bg-black px-5 py-2 text-xs font-bold uppercase tracking-wider text-white hover:bg-major-red hover:border-major-red transition-colors shadow-flat"
          >
            Launch Tools
          </Link>
        </div>
      </div>
    </header>
  );
}
