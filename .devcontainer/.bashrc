parse_git_branch() {
     git branch 2> /dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/ (\1)/'
}

export PS1="[\A] \[\033[38;5;32m\]\u@\H \[\033[38;5;214m\]\w \[\033[38;5;79m\]$(parse_git_branch)\[\033[38;5;11m\]\n\$ \e[m"
