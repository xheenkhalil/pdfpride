import Link from "next/link";
import { FaFilePdf } from "@/components/ui/icons";

export function Footer() {
  return (
    <footer className="border-t-2 border-black bg-white text-black">
      <div className="mx-auto max-w-7xl px-4 py-14 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-10">
          <div className="md:col-span-1 space-y-3">
            <div className="flex items-center gap-2">
              <div className="h-6 w-6 bg-black text-white flex items-center justify-center">
                <FaFilePdf className="h-3.5 w-3.5" />
              </div>
              <span className="text-base font-black tracking-tight uppercase font-mono">
                PDF<span className="text-major-red">PRIDE</span>
              </span>
            </div>
            <p className="text-xs text-neutral-700 leading-relaxed font-medium">
              All your document tools in one place. Merge, split, convert, compress, and edit with maximum speed and zero quality loss.
            </p>
          </div>

          <div>
            <h3 className="text-xs font-black uppercase tracking-widest text-black border-b-2 border-black pb-2 mb-4">
              Popular Tools
            </h3>
            <ul className="space-y-2 text-xs font-bold uppercase tracking-wider">
              <li><Link href="/tools/merge-pdf" className="hover:text-major-red">Merge PDF</Link></li>
              <li><Link href="/tools/split-pdf" className="hover:text-major-red">Split PDF</Link></li>
              <li><Link href="/tools/compress-pdf" className="hover:text-major-red">Compress PDF</Link></li>
              <li><Link href="/tools/pdf-to-excel" className="hover:text-major-red">PDF to Excel (XLSX)</Link></li>
              <li><Link href="/tools/pdf-to-word" className="hover:text-major-red">PDF to Word (DOCX)</Link></li>
              <li><Link href="/tools/image-to-favicon" className="hover:text-major-blue">Favicon Studio</Link></li>
            </ul>
          </div>

          <div>
            <h3 className="text-xs font-black uppercase tracking-widest text-black border-b-2 border-black pb-2 mb-4">
              Document Studio
            </h3>
            <ul className="space-y-2 text-xs font-bold uppercase tracking-wider">
              <li><Link href="/tools" className="hover:text-major-red">All 440 Tools</Link></li>
              <li><Link href="/workspace" className="hover:text-major-red">Cloud Workspace</Link></li>
              <li><Link href="/tools?category=pdf-conversion" className="hover:text-major-red">Document Converters</Link></li>
              <li><Link href="/tools?category=image-studio" className="hover:text-major-red">Image Utilities</Link></li>
            </ul>
          </div>

          <div>
            <h3 className="text-xs font-black uppercase tracking-widest text-black border-b-2 border-black pb-2 mb-4">
              Privacy First
            </h3>
            <p className="text-xs text-neutral-700 leading-relaxed font-medium">
              Your files stay 100% private. All uploaded documents are automatically cleaned up immediately after your task completes.
            </p>
          </div>
        </div>

        <div className="mt-12 border-t-2 border-black pt-6 flex flex-col sm:flex-row items-center justify-between text-[11px] font-mono uppercase tracking-wider text-neutral-600">
          <p>© {new Date().getFullYear()} PDF PRIDE. ALL RIGHTS RESERVED.</p>
          <p className="mt-2 sm:mt-0 font-bold text-black">
            FAST • PRIVATE • PRECISE DOCUMENT TOOLS
          </p>
        </div>
      </div>
    </footer>
  );
}
