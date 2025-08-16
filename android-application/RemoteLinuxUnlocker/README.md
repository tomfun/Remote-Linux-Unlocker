# Install OpenJDK 8:
sudo apt install openjdk-17-jdk

Check available Java versions:
sudo update-alternatives --config java

This will show all installed Java versions and let you select which one to use as default.

For IntelliJ IDEA specifically:
- File → Project Structure → Project Settings → Project
- Set "Project SDK" to Java 17
- This overrides system default for this project only

```bash
/usr/lib/jvm/java-17-openjdk-amd64/bin/java -version
#openjdk version "1.8.0_462"
#OpenJDK Runtime Environment (build 1.8.0_462-8u462-ga~us1-0ubuntu2~22.04.2-b08)
#OpenJDK 64-Bit Server VM (build 25.462-b08, mixed mode)
JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export JAVA_HOME
```

Open SDK settings:
File | Settings | Languages & Frameworks | Android SDK Updater
Install SDK (click on Edit). It will create [local.properties](local.properties) file with:
sdk.dir=/home/tomfun/.jdks/openjdk-24.0.2

# Gradle

./gradlew
./gradlew tasks