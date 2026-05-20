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
        versionCode = 1
        versionName = "5.0.0"
        multiDexEnabled = true
    }

    buildTypes {
        release {
            isDebuggable = false
            isMinifyEnabled = true
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
