"""Helper functions/classes related to secrets (e.g. passwords)."""

from typing import Iterable

from . import shell


def get_secret(
    key: str,
    *key_parts: str,
    cmd_list: Iterable[str] = None,
    folder: str = None,
    user: str = None,
) -> str:
    """Returns a secret (i.e. a password).

    Args:
        key: The key that the secret is associated with.
        key_parts: If provided, these are treated as part of the secret key and
          are joined with the ``key`` argument by separating each distinct key
          part with a period.
        cmd_list: Optional command list to use for fetching the secret (e.g.
          ["pass", "show"], which is the default). Note: we will append the
          ``key`` argument to this list before running.
        folder: If provided, this folder name is prepended to the beginning of
          the ``key`` argument.
        user: Should we use `sudo -u <user>` to run our secret retriever
          command as that user?
    """
    if key_parts:
        key = ".".join([key] + list(key_parts))

    if cmd_list is None:
        cmd_list = ["pass", "show"]

    if folder is not None:
        folder = folder.rstrip("/")
        key = f"{folder}/{key}"

    full_cmd_list = []
    if user is not None:
        full_cmd_list.extend(["sudo", "-u", user])

    full_cmd_list.extend(cmd_list)
    full_cmd_list.append(key)

    secret, _err = shell.safe_popen(full_cmd_list).unwrap()
    return secret
