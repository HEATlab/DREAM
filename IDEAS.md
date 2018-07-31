# Ideas

This file is here for things we want to try, and things we have tried.

## Done

### Surprisal-based DREA (2018)

*Goal*
If we fall outside of SREA's bounds, we reschedule. Otherwise, keep the SREA
bounds.

*Result*
Had similar results to AR with a moderately high threshold, but not tunable. We
decided AR was better anyways.

### DREA-AR which accumulates risk (2018)

*Goal*
Create an alternate version of DREA-AR which accumulates risk, rather than one
which counts contingent edges.

*Result*
I made DREA-ARA which does this. The result isn't too interesting. Its
performance is roughly DREA-AR already. The biggest difference was the curve
shap was different.

### Decoupling by maximising interagent flexibility (2018)

*Goal*
Use an LP which maximises interagent flexibility, and then decouple with those
constraints.

*Result*
dmontsim supports it, but it has some bugs here and there. Plus, it doesn't
have higher robustness than SREA in general. That's because it makes
sub-optimal interval increases. We trade robustness for flexibility, which
doesn't help us. It may be an artefact of the randomly generated problems we
use.

### Decoupling by SREA edge extraction (2018)

*Goal*
Use SREA's LP to generate good decoupling constraints, and apply those to
decouple only agents.

*Result*
dmontsim now supports it. It seems overly restrictive, and barely performs any
different than SREA at any point. May be worth looking into more though. Try
different problems!

