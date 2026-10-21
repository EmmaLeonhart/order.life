-- Used when the PDF is built from the EPUB (Emma, 2026-10-15: "the PDF would be built from the EPUB"):
-- pandoc reads the EPUB's hidden navigation (<nav> ... </nav>, the "landmarks" list) in as text, with links to
-- anchors that no longer exist. This drops it, so the PDF holds only the book.
--
-- It also lays the book out (Emma, 2026-10-19): "the PDF generation always has page breaks between the chapters",
-- and "each book, like all the 13 months, should have their own covers ... We'll just have blank cover things for
-- now", to become something more elaborate later, probably with AI art. So each month (a level-1 heading) starts on
-- a cover page of its own, with its art and its book's name (2026-10-20), and each chapter (level 2) starts a new page,
-- with its own art under the heading.
--   pandoc gaiad.epub -f epub --lua-filter scripts/epub_to_pdf.lua --toc --pdf-engine=typst -o gaiad.pdf

local function typst(text)
  return pandoc.RawBlock("typst", text)
end

local function esc(s)
  return (s:gsub("([\\#%[%]%*_`$<>@\"])", "\\%1"))
end

local function file_exists(path)
  local f = io.open(path, "rb")
  if f then f:close() return true end
  return false
end

local function cover(heading)
  -- The cover of one book: its art (static/covers/<month>.jpg, made with a local free model) above the month's name
  -- and the book's name ("Leo: The Book of Lehi").
  local month, book = heading:match("^(.-):%s*(.+)$")
  month = month or heading
  local art = "static/covers/" .. month:lower() .. ".jpg"
  local img = file_exists(art) and ('#image("/' .. art .. '", height: 60%)\n#v(1.5em)\n') or ""
  local sub = book and ("\n#v(0.5em)\n#text(size: 18pt, style: \"italic\")[" .. esc(book) .. "]") or ""
  return typst("#pagebreak(weak: true)\n#page(header: none, footer: none)[#align(center + horizon)[\n" .. img
               .. "#text(size: 36pt)[" .. esc(month) .. "]" .. sub .. "]]")
end

-- Portraits (Emma, 2026-10-20: "PDF, first mention"; scripts/make_portraits.py): {chapter: {{file, name}, ...}},
-- each person at the first chapter their Gaiad character file (Gaiad/genealogy/<slug>.json) cites or mentions.
local function portraits_by_chapter()
  local out, f = {}, io.open("static/portraits/index.tsv", "r")
  if not f then return out end
  f:read("l")
  for row in f:lines() do
    local file, name, match = row:match("^([^\t]+)\t([^\t]+)\t(.+)$")
    local first
    for slug in (match or ""):gmatch("[^,]+") do
      local g = io.open("Gaiad/genealogy/" .. slug .. ".json", "r")
      if g then
        local d = pandoc.json.decode(g:read("a"), false)
        g:close()
        for _, c in ipairs(d.citations or {}) do
          if not first or c.chapter < first then first = c.chapter end
        end
        for _, n in ipairs(d.chapters_mentioned_in or {}) do
          if not first or n < first then first = n end
        end
      end
    end
    if first then
      out[first] = out[first] or {}
      table.insert(out[first], {file, name})
    end
  end
  f:close()
  return out
end

local function portrait_row(list)
  local cells = {}
  for _, p in ipairs(list) do
    cells[#cells + 1] = 'stack(dir: ttb, spacing: 0.4em, image("/static/portraits/thumbs/' .. p[1] .. '", height: 16%), '
                        .. 'text(size: 9pt)[' .. esc(p[2]) .. '])'
  end
  return typst("#align(center)[#stack(dir: ltr, spacing: 1.5em, " .. table.concat(cells, ", ") .. ")]")
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
  local portraits = portraits_by_chapter()
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
        -- Each chapter's art (Emma, 2026-10-20: "art for every single chapter"; scripts/make_chapter_art.py) goes
        -- under its heading.
        local n = tonumber(pandoc.utils.stringify(b.content):match("^Chapter%s+(%d+)"))
        local art = n and string.format("static/chapters/%03d.jpg", n)
        if art and file_exists(art) then
          out[#out + 1] = b
          out[#out + 1] = typst('#align(center)[#image("/' .. art .. '", height: 38%)]')
          if portraits[n] then
            out[#out + 1] = portrait_row(portraits[n])
          end
          goto continue
        end
      end
      out[#out + 1] = b
      ::continue::
    end
  end
  doc.blocks = out
  return doc
end
