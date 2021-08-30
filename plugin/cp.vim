" =============================================================================
" Filename: plugin/cp.nvim
" Author: Nellow Ly
" License: MIT License
" =============================================================================

if argv(0) != 'cp'
  finish
endif
call serverstart('/tmp/cp')
silent !bash -c 'python <sfile>:p:h/cp.py &'

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
hi HD ctermfg=White ctermbg=none
hi NA ctermfg=White ctermbg=DarkGray
hi PD ctermfg=White ctermbg=Gray
hi AC ctermfg=White ctermbg=Green
hi WA ctermfg=White ctermbg=Red
hi RE ctermfg=White ctermbg=Blue
hi TL ctermfg=White ctermbg=Yellow
" Black fg for Sel
hi fHD ctermfg=Black ctermbg=none
hi fPD ctermfg=Black ctermbg=Gray
hi fNA ctermfg=Black ctermbg=DarkGray
hi fAC ctermfg=Black ctermbg=DarkGreen
hi fWA ctermfg=Black ctermbg=Red
hi fRE ctermfg=Black ctermbg=Blue
hi fTL ctermfg=Black ctermbg=Yellow

autocmd VimLeave * :call CpCmd('save_quit()')
