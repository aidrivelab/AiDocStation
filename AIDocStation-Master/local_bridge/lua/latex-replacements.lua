-- LaTeX Replacements Filter V10
-- Improved chemical formula handling with conditional logic

local function apply_smart_replacements(content)
  -- 1. 处理 \xlongequal[lower]{upper} 或 \xlongequal{upper}
  -- 逻辑：如果 upper 为空，则直接替换为 =，否则使用 \stackrel
  content = content:gsub("\\xlongequal%s*(%b[])%s*(%b{})", function(lower, upper)
    local inner = upper:sub(2, -2):gsub("^%s*(.-)%s*$", "%1") -- 去掉 {} 并 trim
    if inner == "" then return "=" end
    return "\\stackrel{" .. inner .. "}{=}"
  end)
  
  content = content:gsub("\\xlongequal%s*(%b{})", function(upper)
    local inner = upper:sub(2, -2):gsub("^%s*(.-)%s*$", "%1")
    if inner == "" then return "=" end
    return "\\stackrel{" .. inner .. "}{=}"
  end)

  -- 2. 处理 \xrightleftharpoons[lower]{upper}
  -- 逻辑：尽可能保留 upper 文字
  content = content:gsub("\\xrightleftharpoons%s*%b[]%s*(%b{})", function(upper)
    local inner = upper:sub(2, -2):gsub("^%s*(.-)%s*$", "%1")
    if inner == "" then return "\\rightleftharpoons" end
    return "\\stackrel{" .. inner .. "}{\\rightleftharpoons}"
  end)
  
  content = content:gsub("\\xrightleftharpoons%s*(%b{})", function(upper)
    local inner = upper:sub(2, -2):gsub("^%s*(.-)%s*$", "%1")
    if inner == "" then return "\\rightleftharpoons" end
    return "\\stackrel{" .. inner .. "}{\\rightleftharpoons}"
  end)

  -- 3. 其他简单映射
  local simple_mappings = {
    { pattern = "{\\kern%s*[^}]+}", replacement = "\\qquad" },
    { pattern = "\\kern%s*%-?%d*%.?%d+%a%a", replacement = "\\qquad" },
    { pattern = "\\xlongequal", replacement = "=" },
    { pattern = "\\xrightleftharpoons", replacement = "\\rightleftharpoons" },
    { pattern = "\\xlongleftarrow", replacement = "\\longleftarrow" },
    { pattern = "\\xlongrightarrow", replacement = "\\longrightarrow" },
  }

  for _, rule in ipairs(simple_mappings) do
    content = content:gsub(rule.pattern, rule.replacement)
  end

  return content
end

return {
  {
    Math = function(el)
      el.text = apply_smart_replacements(el.text)
      return el
    end
  }
}