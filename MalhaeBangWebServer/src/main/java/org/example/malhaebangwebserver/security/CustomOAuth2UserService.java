package org.example.malhaebangwebserver.security;

import lombok.extern.slf4j.Slf4j;
import lombok.RequiredArgsConstructor;
import org.example.malhaebangwebserver.model.entity.User;
import org.example.malhaebangwebserver.model.enums.LoginType;
import org.example.malhaebangwebserver.repository.UserRepository;
import org.springframework.security.oauth2.client.userinfo.*;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.security.oauth2.core.OAuth2AuthenticationException;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
public class CustomOAuth2UserService implements OAuth2UserService<OAuth2UserRequest, OAuth2User> {

    private final UserRepository userRepository;

    @Override
    public OAuth2User loadUser(OAuth2UserRequest request) throws OAuth2AuthenticationException {
        log.info("✅ [OAuth2] CustomOAuth2UserService 실행됨");

        OAuth2UserService<OAuth2UserRequest, OAuth2User> delegate = new DefaultOAuth2UserService();
        OAuth2User oauth2User = delegate.loadUser(request);

        String registrationId = request.getClientRegistration().getRegistrationId(); // ex: "kakao","naver", "google"
        Map<String, Object> attributes = oauth2User.getAttributes();

        log.info("🔎 registrationId = {}", registrationId);
        log.info("🔎 attributes = {}", attributes);

        String email = null;
        String nickname = null;

        try {
            if (registrationId.equals("kakao")) {
                Map<String, Object> kakaoAccount = (Map<String, Object>) attributes.get("kakao_account");
                Map<String, Object> profile = (Map<String, Object>) kakaoAccount.get("profile");
                email = (String) kakaoAccount.get("email");
                nickname = (String) profile.get("nickname");

            } else if (registrationId.equals("naver")) {
                Map<String, Object> response = (Map<String, Object>) attributes.get("response");
                email = (String) response.get("email");
                nickname = (String) response.get("name");
                attributes = response;

            } else if (registrationId.equals("google")) {
                email = (String) attributes.get("email");
                nickname = (String) attributes.get("name");
            }
            else {
                throw new OAuth2AuthenticationException("지원하지 않는 OAuth 로그인입니다.");
            }

            log.info("📧 email = {}", email);
            log.info("🙋 nickname = {}", nickname);

            Optional<User> existingUser = userRepository.findByUserEmail(email);

            User user;
            if (existingUser.isPresent()) {
                user = existingUser.get();

                if (!user.getLoginType().name().equalsIgnoreCase(registrationId)) {
                    throw new OAuth2AuthenticationException("ALREADY_REGISTERED_WITH_" + user.getLoginType());
                }

                log.info("✅ 기존 유저 로그인: {}", user.getUserEmail());
            }


            else {
                LoginType loginType = switch (registrationId) {
                    case "kakao" -> LoginType.KAKAO;
                    case "naver" -> LoginType.NAVER;
                    case "google" -> LoginType.GOOGLE;
                    default -> throw new IllegalStateException("Unexpected provider: " + registrationId);
                };
                user = User.builder()
                        .userEmail(email)
                        .userNickname(generateUniqueNickname(nickname))
                        .userPw(UUID.randomUUID().toString())
                        .createdAt(LocalDateTime.now())
                        .isDeleted(false)
                        .loginType(loginType)
                        .build();
                userRepository.save(user);
                log.info("🆕 새 유저 저장 완료: {}", user.getUserEmail());
            }

            return new CustomUserDetails(user, attributes);
        } catch (Exception e) {
            log.error("❌ [OAuth2] 사용자 정보 처리 중 오류 발생", e);
            throw new OAuth2AuthenticationException(registrationId.toUpperCase() + " 사용자 정보 파싱 실패");
        }
    }

    private String generateUniqueNickname(String baseNickname) {
        return baseNickname + "_" + UUID.randomUUID().toString().substring(0, 8);
    }
}