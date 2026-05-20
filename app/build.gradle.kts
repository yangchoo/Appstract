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
        versionCode = 2
        versionName = "5.0.1"
        // Keep app/src/main/res/xml/themeinfo.xml in sync (Atom Launcher metadata).
        multiDexEnabled = true
    }

    buildTypes {
        release {
            isDebuggable = false
            isMinifyEnabled = true
            // Sign with debug key so GitHub release APKs are sideloadable.
            // F-Droid builds from source and signs with its own key.
            signingConfig = signingConfigs.getByName("debug")
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

    java {
        toolchain {
            languageVersion.set(JavaLanguageVersion.of(17))
        }
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
