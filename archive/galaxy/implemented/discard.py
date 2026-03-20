import os
from implemented.main_datas import backup_data, original


def discard_dummy_datas():
    # discarding .nomedia
    for _set in (backup_data.set_file_copy, backup_data.set_file_renew):
        to_discard = set()
        for i in _set:
            org = os.path.join(original.path, i)
            base = os.path.basename(org)
            if base == ".nomedia":
                to_discard.add(i)

        _set.difference_update(to_discard)