# 1단계: Build Stage
FROM gradle:8.5-jdk17 AS build
WORKDIR /app

# Gradle 캐시 디렉토리 지정
COPY .gradle /home/gradle/.gradle
ENV GRADLE_USER_HOME=/home/gradle/.gradle

# Gradle 의존성 캐싱을 위해 설정 파일 먼저 복사
COPY build.gradle settings.gradle gradlew ./
COPY gradle ./gradle
RUN chmod +x ./gradlew && ./gradlew dependencies

# 이후 소스코드 복사
COPY src ./src

# 빌드
RUN ./gradlew build -x test

# 2단계: Run Stage
FROM openjdk:17-jdk-slim-buster
WORKDIR /app

# 위 단계에서 빌드한 JAR 파일 복사
COPY --from=build /app/build/libs/*.jar app.jar

# 실행
ENTRYPOINT ["java", "-jar", "app.jar"]