# Installed native libraries only. A different version is a new validation run.
userlib <- Sys.getenv("R_LIBS_USER")
if(nzchar(userlib)) .libPaths(c(strsplit(userlib,.Platform$path.sep,fixed=TRUE)[[1]],.libPaths()))
print(.libPaths())
expected <- c(metafor="5.2.1", meta="8.5.0", metadat="1.6.0", lme4="2.0.6", jsonlite="2.0.0")
stopifnot(as.character(getRversion())=="4.6.0")
for(pkg in names(expected)) {
  if(!requireNamespace(pkg,quietly=TRUE)) stop("Missing installed package: ",pkg)
  actual <- as.character(packageVersion(pkg))
  cat(pkg, actual, "\n")
  if(actual != expected[[pkg]]) stop("Wrong package version: ",pkg)
}
cat("NATIVE PREFLIGHT PASS: R 4.6.0; metafor 5.2-1; meta 8.5-0; metadat 1.6-0; lme4 2.0-6; jsonlite 2.0.0\n")
