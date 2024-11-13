from fastagency import FastAgency
from fastagency.ui.mesop import MesopUI

from ..workflow import wf

app = FastAgency(
    provider=wf,
    ui=MesopUI(),
    title="Context Leakage Team",
)

# start the fastagency app with the following command
# gunicorn context_leakage_team.local.main_mesop:app
