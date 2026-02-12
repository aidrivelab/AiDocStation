-- High Performance Paragraph Mapper (Universal AST Coverage)
-- This version replaces Div wrapping with direct attribute injection to ensure structure purity.

local target_body_style = nil

-- Style Map: 将中文样式名映射到英文 Style ID
-- 这样 Word 可以正确合并到目标文档的内置样式，避免创建 "样式名1" 的重复样式
local style_map = {
  -- 中文名 -> 英文 Style ID
  ['正文'] = 'Normal',
  ['正文文本'] = 'Body Text',
  ['正文缩进'] = 'Body Text Indent',
  ['正文文本缩进'] = 'Body Text Indent',
  ['正文首行缩进'] = 'Body Text First Indent',
  -- 英文名保持不变
  ['Normal'] = 'Normal',
  ['Body Text'] = 'Body Text',
  ['Body Text Indent'] = 'Body Text Indent',
  ['Body Text First Indent'] = 'Body Text First Indent'
}

function Meta(m)
  -- Capture target style from multiple potential metadata keys
  -- [Fix] PANDOC_DOCUMENT_METADATA can be nil if no metadata is passed
  local global_meta = PANDOC_DOCUMENT_METADATA or {}
  local raw = m.body_style or m['body-style'] or global_meta['body-style']
  
  if raw then
    local s = pandoc.utils.stringify(raw)
    target_body_style = style_map[s] or s
  end
  return m
end

-- Universal styling function for any block/inline that supports attributes
local function apply_style(el)
  if not target_body_style or target_body_style == "" then
    return el
  end
  
  -- Inject custom-style (Pandoc's native way to define Word paragraph styles)
  -- This approach avoids OXML nesting issues caused by Div wrapping.
  if not el.attributes['custom-style'] then
    el.attributes['custom-style'] = target_body_style
  end
  return el
end

-- Hook into block-level elements
function Para(el) return apply_style(el) end
function Plain(el) return apply_style(el) end

-- Handle lists recursively to ensure items inherit the mapping
function BulletList(items)
  return items:walk {
    Para = Para,
    Plain = Plain
  }
end

function OrderedList(items)
  return items:walk {
    Para = Para,
    Plain = Plain
  }
end