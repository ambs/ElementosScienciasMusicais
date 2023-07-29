-- Pandoc filter to process code blocks with class "abc" containing
-- ABC notation into images.
--
-- * Assumes that abcm2ps and ImageMagick's convert are in the path.
-- * For textual output formats, use --extract-media=abc-images
-- * For HTML formats, you may alternatively use --embed-resources

local filetypes = { html = {"png", "image/png"}
                  , latex = {"pdf", "application/pdf"}
                  }
local filetype = filetypes[FORMAT][1] or "png"
local mimetype = filetypes[FORMAT][2] or "image/png"

local function abc2eps(abc, filetype)
    local eps = pandoc.pipe("abcm2ps", { "-q", "-O", "-", "-"}, abc)
    local final
    if FORMAT == "latex" then
        local pdf = pandoc.pipe("epstopdf", {"--filter"}, eps)
        local crop_pdf = pandoc.pipe("pdfcrop", {"-", "__.pdf"}, pdf)
        final = pandoc.pipe("cat", {"__.pdf"}, crop_pdf)
        os.remove("__.pdf")
    else
        final = pandoc.pipe("convert", {"-trim", "-", filetype .. ":-"}, eps)
    end
    return final
end

local function generateLaTeX(meta, filename)
    -- caption = meta["caption"] or ""
    -- if caption ~= "" then
    --     caption = "\\caption{" .. caption .. "}\n"
    -- end
    local content = "\\begin{center}\n\\includegraphics{" .. filename .. "}\n\\end{center}"
    return pandoc.RawBlock('latex', content)
end

function CodeBlock(block)
    if block.classes[1] == "abc" then
        local img = abc2eps(block.text, filetype)
        local fname = pandoc.sha1(img) .. "." .. filetype
        pandoc.mediabag.insert(fname, mimetype, img)
        if FORMAT == "latex" then
            return generateLaTeX(block.attributes, fname)
        else
            return pandoc.Para{ pandoc.Image({pandoc.Str("abc tune")}, fname) }
        end
    end
end
