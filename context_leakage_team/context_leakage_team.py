from fastagency import FastAgency
from fastagency.ui.mesop import MesopUI

from context_leakage_team.workflow import wf

app = FastAgency(provider=wf, ui=MesopUI(), title="Context leak chat")
