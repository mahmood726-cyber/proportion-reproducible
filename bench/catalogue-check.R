source('json-writer.R')
mf<-data(package='metafor')$results
writeLines(js(list(metafor_catalogue_entries=nrow(mf),items=if(nrow(mf))as.list(mf[,'Item']) else list())),'metafor-catalogue.json')
cat(nrow(mf),'datasets in metafor package catalogue\n')
