" =============================================================================
" Filename: plugin/cp.nvim
" Author: Nellow Ly
" License: MIT License
" =============================================================================

if argv(0) != 'cp'
  finish
endif
call serverstart('/tmp/cp')
" silent !bash -c 'python <sfile>:p:h/cp.py &'

function CpCmd(s, ...)
py3 << EOF
import socket, vim
s = socket.socket()
s.connect(('127.0.0.1', 11713))
s.sendall(vim.eval('a:s').encode())
EOF
endfunction

function CpTab(num, clicks, button, flags)
  call CpCmd('tab(' . a:num . ')')
endfunction

function CpTest(num, clicks, button, flags)
  if a:button == 'r'
    call CpCmd('problem[cur].hide_show(' . a:num . ')')
  else
    call CpCmd('problem[cur].test(' . a:num . ')')
  endif
endfunction

" Define colors
hi HD ctermfg=White ctermbg=none guifg=#ffffff guibg=none
hi NA ctermfg=White ctermbg=DarkGray guifg=#ffffff guibg=#ABB2BF
hi PD ctermfg=White ctermbg=Gray guifg=#C678DD guibg=#ffffff
hi AC ctermfg=White ctermbg=Green guifg=#ffffff guibg=#98C379
hi WA ctermfg=White ctermbg=Red guifg=#ffffff guibg=#E06C75
hi RE ctermfg=White ctermbg=Blue guifg=#ffffff guibg=#61AFEF
hi TL ctermfg=White ctermbg=Yellow guifg=#ffffff guibg=#E5C07B
" Black fg for Sel
hi fHD ctermfg=Black ctermbg=none guifg=#000000 guibg=none
hi fPD ctermfg=Black ctermbg=Gray guifg=#000000 guibg=#ABB2BF
hi fNA ctermfg=Black ctermbg=DarkGray guifg=#000000 guibg=#ABB2BF
hi fAC ctermfg=Black ctermbg=DarkGreen guifg=#000000 guibg=#98C379
hi fWA ctermfg=Black ctermbg=Red guifg=#000000 guibg=#E06C75
hi fRE ctermfg=Black ctermbg=Blue guifg=#000000 guibg=#61AFEF
hi fTL ctermfg=Black ctermbg=Yellow guifg=#000000 guibg=#E5C07B
hi TabLineFill guibg=none

autocmd VimLeave * :call CpCmd('save_quit()')
