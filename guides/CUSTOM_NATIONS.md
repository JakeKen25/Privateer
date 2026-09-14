# Custom Nation Maker

Privateer's Custom Nation Maker creates a self-contained folder that can be
copied into an installed copy of Rule the Waves 3. It does not edit a campaign
save and it does not change the game installation during export.

## Generated files

RTW3 uses different custom-nation definitions by campaign era. The maker writes
both forms:

- `Data/<Nation>.n00` for 1890 and 1900 starts.
- `Data/<Nation>.n20` for 1920 and 1935 starts.
- `Data/<Nation>ShipNames.dat` and `Data/<Nation>ShipNames20.dat`.
- `Data/<Nation>Names.txt` for generated officer names.
- `Data/<Nation>WarInfo.dat` and `Data/<Nation>WarInfo20.dat`.
- Four 60×40 Windows BMP files under `Flags` for the normal, fascist,
  communist, and republican flag fields.
- `INSTALL.txt` and `privateer-nation.json` at the package root.

Every default ship name uses the ship type and a sequence number, such as
`BB-01`, `KE-05`, or `CV-30`. The output covers BB, BC, CA, CL, DD, KE, AMC,
CV, CVL, SS, and XX lists.

## Template inheritance

A custom nation must refer to possessions that exist in the installed game's
`MapData` files. The current maker therefore starts from a stock template and
preserves its possessions, relationships, bonus technology, obscure AI values,
and unfamiliar fields. The identity, leaders, economy, government, common
traits, research advantages, gun quality, flags, and generated names can be
changed.

The corresponding stock WarInfo files are copied under the custom nation's name.
This produces a usable package without committing or redistributing game data in
the Privateer repository.

Creating new territory or changing the strategic map remains a separate advanced
task. A nation that needs different possessions must also receive coordinated
changes to every applicable `MapData*.dat` file and may require new battle and
waypoint coordinates.

## Installation and testing

1. Close Rule the Waves 3.
2. Back up the installed `Data` and `Flags` folders.
3. Copy the generated package's `Data` files into RTW3's `Data` folder.
4. Copy the generated package's `Flags` files into RTW3's `Flags` folder.
5. Start a new campaign and select the nation from the custom-nation list.
6. Check nation selection, starting possessions, budget, initial fleet, ship-name
   generation, and flag changes after government transitions.

Existing campaigns are not converted. Keep the generated package so its files
can be identified during updates or uninstalling.

## Research basis and limits

The implementation was checked against the supplied Byzantine Empire, Holy
Roman Empire, and Ottoman nation mods; the installed RTW3 1.01.44 data files;
the NWS custom-nation discussions; and the community RTW3 data-editing guide.
Community reports confirm that `.n00` serves both 1890 and 1900 while `.n20`
serves both 1920 and 1935. They also document that nation additions span nation
definitions, ship and officer names, WarInfo, flags, and often MapData.

Sources:

- https://nws-online.proboards.com/thread/8182/nation-mod-holy-roman-empire
- https://nws-online.proboards.com/thread/6955/nation-mod-ottomans
- https://wikiwiki.jp/rulethewaves/RTW3%20%E5%9B%BD%E5%AE%B6%E3%83%87%E3%83%BC%E3%82%BF%E8%A7%A3%E8%AA%AC

These formats are unofficial and may change in later RTW3 patches. Test packages
against a new campaign before relying on them.

