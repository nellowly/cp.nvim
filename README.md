
# cp.nvim

neovim plugin for cp

# Features

- Problem parser
- Multiple problem
- Extensive multitest
- Hotkey submit
- Stresstest
- Terminal intergration
- GDB support

# Config

.vimrc example

```vim
"/ cp.nvim config
if argv(0) == 'cp'
  for i in range(0, 9)
    execute "noremap <A-" . i . "> :call CpCmd('tab(" . i . ")')<CR>"
  endfor
  noremap <A-t> :2wincmd w \| term<CR>i
  noremap <A-S> :call CpCmd('problem[cur].submit()')<CR>
  noremap <A-c> :wa \| call CpCmd('problem[cur].compile()')<CR>
  noremap <A-r> :wa \| call CpCmd('threading.Thread(target = problem[cur].run(problem[cur].curTest).start())')<CR><CR>
  noremap <A-a> :wa \| call CpCmd('threading.Thread(target = problem[cur].compile_run).start()')<CR><CR>
  noremap <A-d> :call CpCmd('problem[cur].remove(problem[cur].curTest)')<CR>
  noremap <A-s> :call CpCmd('problem[cur].hide_show(problem[cur].curTest)')<CR>
  noremap <A-m> :call CpCmd('problem[cur].show_all()')<CR>
  noremap <A-o> :call CpCmd('problem[cur].hide("AC")')<CR>
  noremap <A-i> :call CpCmd('problem[cur].invert()')<CR>
  noremap t :<C-u>call CpTest(v:count, 1, 'l', 0)<CR>
  function CpAdd(...)
    call CpCmd('problem[cur].add(' . v:count .')')
  endfunction
  noremap A :<C-u>call CpAdd()<CR>
endif
"\
```

