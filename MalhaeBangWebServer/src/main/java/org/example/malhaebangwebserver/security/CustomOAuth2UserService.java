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

        String registrationId = request.getClientRegistration().getRegistrationId(); // ex: "kakao"
        Map<String, Object> attributes = oauth2User.getAttributes();

        log.info("🔎 registrationId = {}", registrationId);
        log.info("🔎 attributes = {}", attributes);

        try {
            Map<String, Object> kakaoAccount = (Map<String, Object>) attributes.get("kakao_account");
            Map<String, Object> profile = (Map<String, Object>) kakaoAccount.get("profile");

            String email = (String) kakaoAccount.get("email");
            String nickname = (String) profile.get("nickname");

            log.info("📧 email = {}", email);
            log.info("🙋 nickname = {}", nickname);

            Optional<User> existingUser = userRepository.findByUserEmail(email);

            User user;
            if (existingUser.isPresent()) {
                user = existingUser.get();
                log.info("✅ 기존 유저 로그인: {}", user.getUserEmail());
            } else {
                user = User.builder()
                        .userEmail(email)
                        .userNickname(generateUniqueNickname(nickname))
                        .userPw(UUID.randomUUID().toString())
                        .userPhone("000-0000-0000")
                        .createdAt(LocalDateTime.now())
                        .isDeleted(false)
                        .loginType(LoginType.KAKAO)
                        .build();
                userRepository.save(user);
                log.info("🆕 새 유저 저장 완료: {}", user.getUserEmail());
            }

            return new CustomUserDetails(user, attributes);
        } catch (Exception e) {
            log.error("❌ [OAuth2] 사용자 정보 처리 중 오류 발생", e);
            throw new OAuth2AuthenticationException("카카오 사용자 정보 파싱 실패");
        }
    }

    private String generateUniqueNickname(String baseNickname) {
        return baseNickname + "_" + UUID.randomUUID().toString().substring(0, 8);
    }
}