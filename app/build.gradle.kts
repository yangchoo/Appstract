plugins {
    id("com.android.application")
}

android {
    namespace = "dev.appstract.iconpack"
    compileSdk = 36

    defaultConfig {
        applicationId = "dev.appstract.iconpack"
        minSdk = 21
        targetSdk = 36
        versionCode = 7
        versionName = "5.0.6"
        // Keep app/src/main/res/xml/themeinfo.xml in sync (Atom Launcher metadata).
        multiDexEnabled = true
    }

    // Don't embed the AGP "Dependency metadata" blob in the APK signing block.
    // F-Droid's scanner rejects extra signing blocks (and it isn't reproducible).
    dependenciesInfo {
        includeInApk = false
        includeInBundle = false
    }

    // Stable release signing key, supplied via environment variables in CI
    // (see .github/workflows/release.yml). Required for F-Droid reproducible
    // builds: the published APK must carry a consistent signing certificate so
    // it can be matched against AllowedAPKSigningKeys in fdroiddata. Falls back
    // to the debug key for local builds when the env vars are absent.
    val releaseStoreFile: String? = System.getenv("RELEASE_STORE_FILE")
    signingConfigs {
        create("release") {
            if (releaseStoreFile != null) {
                storeFile = file(releaseStoreFile)
                storePassword = System.getenv("RELEASE_STORE_PASSWORD")
                keyAlias = System.getenv("RELEASE_KEY_ALIAS")
                keyPassword = System.getenv("RELEASE_KEY_PASSWORD")
            }
        }
    }

    buildTypes {
        release {
            isDebuggable = false
            isMinifyEnabled = true
            signingConfig = if (releaseStoreFile != null) {
                signingConfigs.getByName("release")
            } else {
                signingConfigs.getByName("debug")
            }
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro",
            )
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    bundle {
        language {
            enableSplit = false
        }
    }
}

dependencies {
    implementation("com.github.Donnnno:candybar-foss:3.23.0")
}

val copyIcons = tasks.register<Copy>("copyIcons") {
    from("${rootProject.projectDir}/icons/appstract-dark")
    into("$projectDir/src/main/res/drawable-nodpi")
    include("*.png")
}

val copyXMLs = tasks.register<Copy>("copyXMLs") {
    from("$projectDir/src/main/res/xml") {
        include("appfilter.xml", "drawable.xml")
    }
    into("$projectDir/src/main/assets/")
}

tasks.configureEach {
    if (name == "preBuild") {
        dependsOn(copyIcons, copyXMLs)
    }
}
