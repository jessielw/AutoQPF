def check_for_long_path():
    """If OS is Window's we'll check if long path is enabled"""
    import ctypes

    ntdll = ctypes.WinDLL("ntdll")

    if hasattr(ntdll, "RtlAreLongPathsEnabled"):
        ntdll.RtlAreLongPathsEnabled.restype = ctypes.c_ubyte
        ntdll.RtlAreLongPathsEnabled.argtypes = ()

        def are_long_paths_enabled():
            return bool(ntdll.RtlAreLongPathsEnabled())

        # Call the function to determine if long paths are enabled
        return are_long_paths_enabled()

    else:
        return False
