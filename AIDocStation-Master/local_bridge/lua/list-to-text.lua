-- Pandoc Filter: Flatten Lists to Plain Text Paragraphs
-- This filter converts OrderedList and BulletList into a sequence of normal paragraphs
-- with manual prefixes (1., 2., •) to ensure stability in Microsoft Word.

local function flatten_list(el, is_ordered)
  local blocks = {}
  local start_number = 1
  if is_ordered then
    start_number = el.start or 1
  end

  for i, item_blocks in ipairs(el.content) do
    local prefix_str = ""
    if is_ordered then
      prefix_str = tostring(i + start_number - 1) .. ".\t"
    else
      prefix_str = "•\t"
    end

    -- Inject prefix into the first block of the list item
    local first_block = item_blocks[1]
    if first_block and (first_block.t == "Para" or first_block.t == "Plain") then
      table.insert(first_block.content, 1, pandoc.Str(prefix_str))
    end

    -- Collect all blocks from this item
    for _, b in ipairs(item_blocks) do
      table.insert(blocks, b)
    end
  end
  return blocks
end

function OrderedList(el)
  return flatten_list(el, true)
end

function BulletList(el)
  return flatten_list(el, false)
end
