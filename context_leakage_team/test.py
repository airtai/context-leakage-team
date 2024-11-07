from fastagency import FastAgency
from fastagency.ui.mesop import MesopUI
from workflows import test_wf

app = FastAgency(
    provider=test_wf,
    ui=MesopUI(),
    title="My FastAgency App",
)

# start the fastagency app with the following command
# gunicorn my_fastagency_app.local.main_mesop:app
