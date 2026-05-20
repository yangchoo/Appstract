# Appstract Icon Pack

An abstract Android icon pack with nearly 590 hand-designed icons. Originally created by [Melanie Gutzmann](https://github.com/mirrorkeydev) (mirrorkeydev), this is a community-maintained fork rebuilt for F-Droid using [CandyBar FOSS](https://github.com/Donnnno/candybar-foss).

![Icon Preview](bothimage.png)

## Features

- 590 abstract icons covering popular apps
- Support for Nova, Lawnchair, ADW, Apex, Action, and many other launchers
- Icon request via email
- Wallpapers loaded from GitHub
- Muzei live wallpaper integration

## Build

Requirements: JDK 17, Android SDK (API 36)

```bash
./gradlew assembleRelease
```

The release APK will be at `app/build/outputs/apk/release/`.

Icons are copied from `icons/appstract-dark/` into `app/src/main/res/drawable-nodpi/` at build time. Config XMLs (`appfilter.xml`, `drawable.xml`) are copied to assets automatically.

## F-Droid

This fork is intended for F-Droid submission. Metadata lives in `fastlane/metadata/android/en-US/`.

## Installing

**GitHub Releases** ship debug-signed APKs so they can be sideloaded for testing. **F-Droid** builds from source and signs with its own key.

If you install from GitHub Releases and later switch to F-Droid (or the other way around), Android treats them as different apps because the signatures differ — **uninstall first, then install from the new source**. Icon pack settings do not carry over across reinstall.

Once the app is on F-Droid, prefer installing from there for updates.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for icon design guidelines and contribution instructions.

## Credits

- **Original author:** Melanie Gutzmann (mirrorkeydev) — designed and created all icons
- **Dashboard:** [CandyBar FOSS](https://github.com/Donnnno/candybar-foss) by Donnnno
- **Community fork:** Maintained for F-Droid distribution

## License

All work in this repository is licensed under [Apache 2.0](LICENSE.md).
