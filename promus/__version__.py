"""promus version

version_info conforms to PEP 386

(major, minor, micro, alpha/beta/rc/final, #)
(1, 1, 2, 'alpha', 0) => "1.1.2.dev"
(1, 2, 0, 'beta', 2) => "1.2b2"

"""

VERSION_INFO = (0, 1, 2, 'final', 0)


def get_version():
    """Return a PEP-386 compliant version number from version_info."""
    assert len(VERSION_INFO) == 5
    assert VERSION_INFO[3] in ('alpha', 'beta', 'rc', 'final')

    parts = 2 if VERSION_INFO[2] == 0 else 3
    main = '.'.join([str(part) for part in VERSION_INFO[:parts]])

    sub = ''
    if VERSION_INFO[3] == 'alpha' and VERSION_INFO[4] == 0:
        sub = '.dev'
    elif VERSION_INFO[3] != 'final':
        mapping = {'alpha': 'a', 'beta': 'b', 'rc': 'c'}
        sub = mapping[VERSION_INFO[3]] + str(VERSION_INFO[4])

    return str(main + sub)

VERSION = get_version()
