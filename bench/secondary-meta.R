suppressPackageStartupMessages(library(meta))
source('json-writer.R')
d<-read.csv('meta-input.csv',check.names=FALSE)
refine<-'--refine'%in%commandArgs(TRUE)
if(refine)d<-d[is.na(d$x)|grepl('^dat.crisafulli2020::',d$id),]
out<-list()
for(id in unique(d$id))for(tr in c('logit','ft','raw'))for(method in c('PM','DL','FE')) {
 z<-d[d$id==id & !is.na(d$x),];key<-paste(id,tr,method,sep='|');ww<-character()
 out[[key]]<-tryCatch(withCallingHandlers({
  if(nrow(z)<2)stop('Need at least 2 studies.')
  fit<-metaprop(z$x,z$n,sm=switch(tr,logit='PLOGIT',ft='PFT',raw='PRAW'),method='Inverse',method.tau=if(method=='FE')'DL' else method,method.random.ci='classic',incr=.5,method.incr='only0',method.ci='CP',control=list(tol=1e-18,maxiter=10000))
  # Inspected meta 8.5.0: PFT uses the same half-sum scale as metafor/page.
  scale<-1
  vals<-if(method=='FE')list(mu_re=fit$TE.common/scale,seRE=fit$seTE.common/scale,tau2=0) else list(mu_re=fit$TE.random/scale,seRE=fit$seTE.random/scale,tau2=fit$tau2/scale^2)
  list(status='ok',values=vals)
 },warning=function(w){ww<<-c(ww,conditionMessage(w));invokeRestart('muffleWarning')}),error=function(e)list(status='refused',error=conditionMessage(e)))
 out[[key]]$warnings<-as.list(ww)
 if(length(out)%%300==0)cat(length(out),'meta configurations completed\n')
}
writeLines(js(out),if(refine)'meta-reference-refined.json' else 'meta-reference.json')
cat(length(out),'meta reference configurations written\n')
