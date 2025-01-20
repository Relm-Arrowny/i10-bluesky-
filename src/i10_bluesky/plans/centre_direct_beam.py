from bluesky.plan_stubs import null


def centre_tth(det, start=-1, end=1, num=21):
    yield from null()


def centre_alpha(det, start=-0.8, end=0.8, num=21):
    yield from null()


def centre_det_angles(det):
    yield from centre_tth(det)
    yield from centre_alpha(det)
