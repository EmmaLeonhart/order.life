-- Used when the PDF is built from the EPUB (Emma, 2026-10-15: "the PDF would be built from the EPUB"):
-- pandoc reads the EPUB's hidden navigation (<nav> ... </nav>, the "landmarks" list) in as text, with links to
-- anchors that no longer exist. This drops it, so the PDF holds only the book.
--
-- It also lays the book out (Emma, 2026-10-19): "the PDF generation always has page breaks between the chapters",
-- and "each book, like all the 13 months, should have their own covers ... We'll just have blank cover things for
-- now", to become something more elaborate later, probably with AI art. So each month (a level-1 heading) starts on
-- a cover page of its own, which for now carries only the book's name, and each chapter (level 2) starts a new page.
--   pandoc gaiad.epub -f epub --lua-filter scripts/epub_to_pdf.lua --toc --pdf-engine=typst -o gaiad.pdf

local function typst(text)
  return pandoc.RawBlock("typst", text)
end

local function cover(name)
  -- The placeholder cover: a page of its own with the book's name in the middle. The art goes here later.
  local escaped = name:gsub("([\\#%[%]%*_`$<>@])", "\\%1")
  return typst("#pagebreak(weak: true)\n#page(header: none, footer: none)[#align(center + horizon)[#text(size: 36pt)["
               .. escaped .. "]]]")
end

-- The EPUB reader wraps each month and chapter in a section Div, and Typst allows no page break or page inside a
-- container, so the section Divs are unwrapped first and the headings then stand at the top level.
local function flatten(blocks, out)
  for _, b in ipairs(blocks) do
    if b.t == "Div" and b.classes:includes("section") then
      flatten(b.content, out)
    else
      out[#out + 1] = b
    end
  end
  return out
end

function Pandoc(doc)
  local out, skipping, after_month = {}, false, false
  for _, b in ipairs(flatten(doc.blocks, {})) do
    if b.t == "RawBlock" and b.format == "html" and b.text:match("^<nav") then
      skipping = true
    elseif skipping and b.t == "RawBlock" and b.format == "html" and b.text:match("^</nav>") then
      skipping = false
    elseif not skipping then
      if b.t == "Header" and b.level == 1 then
        out[#out + 1] = cover(pandoc.utils.stringify(b.content))
        out[#out + 1] = typst("#pagebreak(weak: true)")
        after_month = true
      elseif b.t == "Header" and b.level == 2 then
        -- The month's first chapter shares the page with the month's heading; every other chapter starts a page.
        if not after_month then
          out[#out + 1] = typst("#pagebreak(weak: true)")
        end
        after_month = false
      end
      out[#out + 1] = b
    end
  end
  doc.blocks = out
  return doc
end
