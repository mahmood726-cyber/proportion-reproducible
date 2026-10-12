# Refit all numerical reference quantities; installed packages only, no downloads.
main <- function() {
  # Prefer an explicitly supplied user library; keep R_LIBS for dependencies.
  # On this platform R otherwise places R_LIBS ahead of R_LIBS_USER.
  userlib <- Sys.getenv('R_LIBS_USER')
  if(nzchar(userlib)) .libPaths(c(strsplit(userlib,.Platform$path.sep,fixed=TRUE)[[1]],.libPaths()))
  for(pkg in c('metafor','jsonlite')) if(!requireNamespace(pkg,quietly=TRUE)) stop('Required installed package missing: ',pkg)
  suppressPackageStartupMessages(library(metafor))
  cat(R.version.string,'\nmetafor ',as.character(packageVersion('metafor')),'; paper 5.2-1\n',sep='')
  cat('Recomputed: escalc, rma, pooled CI/PI, inverse transforms, yi/vi, study CP limits, proportions and weights.\nReplayed: four archived browser DOM checks per successful fit; no browser is run.\n')
  corpus<-jsonlite::fromJSON('data/corpus.json',simplifyVector=FALSE)
  app<-jsonlite::fromJSON('results/app-patched.json',simplifyVector=FALSE)
  ids<-unlist(lapply(corpus,function(ca)unlist(lapply(c('logit','ft','raw'),function(tr)paste(ca$id,tr,c('PM','DL','FE'),sep='|')))))
  # Coverage gate: 2160 distinct configurations in both inputs; duplicate archived keys would let a conflicting
  # record be silently ignored (app[[key]] returns only the first).
  stopifnot(length(ids)==2160L,!anyDuplicated(ids),length(app)==length(ids),!is.null(names(app)),
            !anyDuplicated(names(app)),setequal(ids,names(app)))
  stats<-list()
  num<-function(x)if(is.null(x))NA_real_ else as.numeric(x)
  check<-function(q,a,b,tol,mode='recomputed R') {
    stopifnot(length(a)==length(b))
    diff<-rep(Inf,length(b));both<-is.na(a)&is.na(b);valid<-is.finite(a)&is.finite(b)
    diff[both]<-0;diff[valid]<-abs(a[valid]-b[valid])/pmax(1,abs(b[valid]))
    z<-stats[[q]];if(is.null(z))z<-list(checks=0,passed=0,max_difference=0,tolerances=numeric(),mode=mode)
    z$checks<-z$checks+length(b);z$passed<-z$passed+sum(diff<=tol);z$max_difference<-max(z$max_difference,diff);z$tolerances<-sort(unique(c(z$tolerances,tol)));stats[[q]]<<-z
  }
  pct<-function(x)sprintf('%.1f%%',100*x)
  percents<-function(s)regmatches(s,gregexpr('[-+]?[0-9]+\\.[0-9]+%',s))[[1]]
  for(ca in corpus)for(tr in c('logit','ft','raw'))for(method in c('PM','DL','FE')) {
    key<-paste(ca$id,tr,method,sep='|');a<-app[[key]]
    x<-vapply(ca$rows,function(z)z$x,0);n<-vapply(ca$rows,function(z)z$n,0);k<-length(x)
    stopifnot(all(is.finite(x)),all(is.finite(n)),all(n>0),all(x>=0&x<=n),all(x==floor(x)),all(n==floor(n)))
    if(k<2) {check('status',as.numeric(a$status=='refused'),1,0);next}
    # Any unexpected R fitting error aborts, rather than being counted as a matched refusal.
    es<-escalc(measure=switch(tr,logit='PLO',ft='PFT',raw='PR'),xi=x,ni=n,add=if(tr=='ft')0 else .5,to='only0')
    fit<-rma(es$yi,es$vi,method=method,test='z',control=list(threshold=1e-12,tol=1e-18,maxiter=10000))
    pred<-predict(fit)
    pi<-if(k>=3)as.numeric(coef(fit))+c(-1,1)*qt(.975,k-1)*sqrt(fit$tau2+fit$se^2) else c(NA,NA)
    back<-switch(tr,logit=transf.ilogit,ft=function(z)transf.ipft.hm(z,targs=list(ni=n)),raw=function(z)pmin(1,pmax(0,z)))
    bp<-predict(fit,transf=back)
    vals<-list(mu_re=as.numeric(coef(fit)),seRE=as.numeric(fit$se),tau2=fit$tau2,Q=fit$QE,df=k-1,i2=max(0,100*(fit$QE-(k-1))/fit$QE),k=k,lo=pred$ci.lb,hi=pred$ci.ub,piLo=pi[1],piHi=pi[2],poolP=bp$pred,poolLo=bp$ci.lb,poolHi=bp$ci.ub,poolPiLo=if(k>=3)back(pi[1]) else NA_real_,poolPiHi=if(k>=3)back(pi[2]) else NA_real_)
    check('status',as.numeric(a$status=='ok'),1,0)
    if(a$status!='ok')stop('Archived app unexpectedly refused ',key)
    stopifnot(length(a$yi)==k,length(a$vi)==k,length(a$studies)==k)
    for(q in names(vals)) {
      stopifnot(q %in% names(a$values))
      tol<-if(method=='PM' && !(q %in% c('Q','df','i2','k')))1e-6 else 1e-9
      check(q,num(a$values[[q]]),num(vals[[q]]),tol)
    }
    check('yi',vapply(a$yi,num,0),es$yi,1e-9);check('vi',vapply(a$vi,num,0),es$vi,1e-9)
    cpLo<-vapply(seq_along(x),function(i)if(x[i]==0)0 else qbeta(.025,x[i],n[i]-x[i]+1),0)
    cpHi<-vapply(seq_along(x),function(i)if(x[i]==n[i])1 else qbeta(.975,x[i]+1,n[i]-x[i]),0)
    study<-list(lo=cpLo,hi=cpHi,rel=weights(fit),p=x/n)
    for(q in names(study))check(paste0('study_',q),vapply(a$studies,function(z)num(z[[q]]),0),study[[q]],if(q=='rel'&&method=='PM')1e-6 else 1e-9)
    mode<-'replayed archived browser DOM versus recomputed R'
    check('ui_row_count',num(a$display$rows),k+1,0,mode);check('ui_forest_diamond',num(a$display$forest),1,0,mode)
    check('ui_pooled_text',as.numeric(identical(percents(a$display$pooled),pct(unlist(vals[c('poolP','poolLo','poolHi')])) |> unname())),1,0,mode)
    shown<-if(grepl('prediction interval = ',a$display$heterogeneity))percents(sub('.*prediction interval = ','',a$display$heterogeneity)) else character()
    expected<-if(k>=3)unname(pct(unlist(vals[c('poolPiLo','poolPiHi')]))) else character()
    check('ui_prediction_text',as.numeric(identical(shown,expected)),1,0,mode)
  }
  table<-do.call(rbind,lapply(names(stats),function(q){s<-stats[[q]];data.frame(quantity=q,checks=s$checks,passed=s$passed,largest_difference=s$max_difference,tolerance=paste(s$tolerances,collapse=';'),Mode=s$mode)}))
  print(table,row.names=FALSE,digits=17)
  dir.create('outputs',showWarnings=FALSE);write.csv(table,'outputs/validate_R_table.csv',row.names=FALSE)
  cat(sprintf('%d/%d checks pass\n',sum(table$passed),sum(table$checks)))
  if(sum(table$checks)!=298116L||sum(table$passed)!=298116L)1L else 0L
}
status<-tryCatch(main(),error=function(e){cat('Validation failed: ',conditionMessage(e),'\n',sep='',file=stderr());1L})
quit(save='no',status=status)
