js <- function(x) {
 if(is.null(x)) return('null')
 if(is.list(x)) { z<-vapply(x,js,''); if(!is.null(names(x))) return(paste0('{',paste(paste0(vapply(names(x),js,''),':',z),collapse=','),'}')); return(paste0('[',paste(z,collapse=','),']')) }
 if(length(x)!=1) return(paste0('[',paste(vapply(as.list(x),js,''),collapse=','),']'))
 if(is.na(x)) return('null')
 if(is.character(x)) return(paste0('"',gsub('\n','\\n',gsub('"','\\"',gsub('\\','\\\\',enc2utf8(x),fixed=TRUE),fixed=TRUE),fixed=TRUE),'"'))
 if(is.logical(x)) return(if(x)'true' else 'false')
 if(!is.finite(x)) return('null')
 sprintf('%.17g',x)
}
