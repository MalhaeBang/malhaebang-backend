# 1단계: Build Stage
FROM gradle:8.5-jdk17 AS build
WORKDIR /app

# 필요한 소스코드 복사
COPY gradlew build.gradle settings.gradle ./
COPY gradle ./gradle
COPY src ./src

# Gradle Wrapper 권한 추가
RUN chmod +x ./gradlew

# 빌드
RUN ./gradlew build -x test

# 2단계: Run Stage
FROM openjdk:17-jdk-slim
WORKDIR /app

# 위 단계에서 빌드한 JAR 파일 복사
COPY --from=build /app/build/libs/*.jar app.jar

# 실행
ENTRYPOINT ["java", "-jar", "app.jar"]