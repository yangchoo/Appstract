-optimizationpasses 5
-overloadaggressively
-dontpreverify
-repackageclasses 'o'
-allowaccessmodification

-keep class **.R
-keep class **.R$* {
    <fields>;
}

-keepattributes SourceFile,LineNumberTable
-renamesourcefileattribute SourceFile

# CandyBar / JSON / networking (library consumer rules may also apply)
-keep class com.bluelinelabs.logansquare.** { *; }
-keep @com.bluelinelabs.logansquare.annotation.JsonObject class *
-keep class **$$JsonObjectMapper { *; }

-dontwarn okhttp3.**
-dontwarn okio.**
-dontwarn javax.annotation.**
-dontwarn org.conscrypt.ConscryptHostnameVerifier

-keep public class * extends com.bumptech.glide.module.AppGlideModule
-keep class com.bumptech.glide.GeneratedAppGlideModuleImpl
