-- Used when the PDF is built from the EPUB (Emma, 2026-10-15: "the PDF would be built from the EPUB"):
-- pandoc reads the EPUB's hidden navigation (<nav> ... </nav>, the "landmarks" list) in as text, with links to
-- anchors that no longer exist. This drops it, so the PDF holds only the book.
--   pandoc gaiad.epub -f epub --lua-filter scripts/epub_to_pdf.lua --toc --pdf-engine=typst -o gaiad.pdf
function Pandoc(doc)
  local out, skipping = {}, false
  for _, b in ipairs(doc.blocks) do
    if b.t == "RawBlock" and b.format == "html" and b.text:match("^<nav") then
      skipping = true
    elseif skipping and b.t == "RawBlock" and b.format == "html" and b.text:match("^</nav>") then
      skipping = false
    elseif not skipping then
      out[#out + 1] = b
    end
  end
  doc.blocks = out
  return doc
end
