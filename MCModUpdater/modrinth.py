import typing
import httpx

from MCModUpdater.resources import constants


async def get_mod_from_slug_async(
        mod_slug: str,
        before_response_funcs: typing.List[typing.Callable] = None,
        after_response_funcs: typing.List[typing.Callable] = None):
    """
    Returns the mod given by the slug. \n
    Returns None if no mod or file was found. \n
    Functions are called before and after making a http request. \n
    """

    timeout = httpx.Timeout(30)
    attempt = 0
    url = f"{constants.MR_API_URL}/project/{mod_slug}"
    async with httpx.AsyncClient(timeout=timeout) as client:
        while True:
            if attempt >= 3:
                print(f"Error: Max attempts made for '{mod_slug}'")
                return

            try:
                if before_response_funcs is not None:
                    request_object = client.build_request(method="GET", url=url)
                    for before_response_func in before_response_funcs:
                        await before_response_func(request_object)

                response = await client.get(url)

                mod = None
                if response.status_code == 200:
                    mod = response.json()

                if after_response_funcs is not None:
                    for response_func in after_response_funcs:
                        await response_func(response, mod)

                return mod
            except httpx.ReadTimeout:
                attempt += 1
                print(f"Error: httpx.ReadTimeout for '{mod_slug}', trying again ({attempt})")
            except httpx.ConnectTimeout:
                attempt += 1
                print(f"Error: httpx.ConnectTimeout for '{mod_slug}', trying again ({attempt})")


async def get_latest_mod_file_async(
        mod_slug: str, game_version: str, mod_loader: str = None,
        before_response_funcs: typing.List[typing.Callable] = None,
        after_response_funcs: typing.List[typing.Callable] = None):
    """
    Returns the latest file that matches the params. \n
    Returns None if no mod or file was found. \n
    Functions are called before and after making a http request. \n
    """

    timeout = httpx.Timeout(30)
    attempt = 0
    url = f"{constants.MR_API_URL}/project/{mod_slug}/version"
    async with httpx.AsyncClient(timeout=timeout) as client:
        while True:
            if attempt >= 3:
                print(f"Error: Max attempts made for '{mod_slug}'")
                return

            try:
                if before_response_funcs is not None:
                    request_object = client.build_request(method="GET", url=url)
                    for before_response_func in before_response_funcs:
                        await before_response_func(request_object)

                response = await client.get(url)

                correct_file = None
                if response.status_code == 200:
                    for file in response.json():
                        has_game_version = game_version in file['game_versions']
                        has_mod_loader = True if mod_loader is None else mod_loader in file['loaders']
                        if has_game_version and has_mod_loader:
                            correct_file = file

                if after_response_funcs is not None:
                    for response_func in after_response_funcs:
                        await response_func(response, correct_file)

                return correct_file
            except httpx.ReadTimeout:
                attempt += 1
                print(f"Error: httpx.ReadTimeout for '{mod_slug}', trying again ({attempt})")
            except httpx.ConnectTimeout:
                attempt += 1
                print(f"Error: httpx.ConnectTimeout for '{mod_slug}', trying again ({attempt})")
