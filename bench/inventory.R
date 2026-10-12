library(metadat)
items <- sort(unique(data(package='metadat')$results[,'Item']))
out <- list()
for (nm in items) {
 e <- new.env(); data(list=nm,package='metadat',envir=e)
 d <- e[[nm]]
 out[[nm]] <- paste(nm, if(is.data.frame(d)) paste(names(d),collapse=' | ') else class(d),sep=': ')
}
writeLines(unlist(out),'inventory.txt')
rd <- tools::Rd_db('metadat')
dir.create('manuals',showWarnings=FALSE)
for(nm in names(rd)) writeLines(capture.output(tools::Rd2txt(rd[[nm]])),file.path('manuals',sub('.Rd','.txt',nm,fixed=TRUE)))
