package org.example.malhaebangwebserver.service;

import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.example.malhaebangwebserver.model.entity.User;
import org.example.malhaebangwebserver.model.enums.LoginType;
import org.example.malhaebangwebserver.repository.UserRepository;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;

import java.time.LocalDateTime;
import java.util.UUID;


@Slf4j
@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    @Transactional
    public void register(String email, String nickname, String password) {
        log.info("🔥 [회원가입 시도] 이메일: {}", email);
        if (userRepository.existsByUserEmail(email)) {
            throw new IllegalArgumentException("이미 존재하는 이메일입니다.");
        }

        User user = User.builder()
                .userEmail(email)
                .userPw(passwordEncoder.encode(password))
                .userNickname(nickname)
                .createdAt(LocalDateTime.now())
                .isDeleted(false)
                .loginType(LoginType.FORM)
                .build();

        log.info("🔥 [회원 생성 직전]");
        userRepository.save(user);
        log.info("✅ [회원 생성 완료]");
    }

    public User findByEmail(String email) {
        return userRepository.findByUserEmail(email)
                .orElseThrow(() -> new IllegalArgumentException("유저를 찾을 수 없습니다."));
    }

    public boolean existsByEmail(String email) {
        return userRepository.existsByUserEmail(email);
    }

    @Transactional
    public String resetPassword(String email) {
        User user = userRepository.findByUserEmail(email)
                .orElseThrow(() -> new IllegalArgumentException("이메일 없음"));

        String tempPassword = UUID.randomUUID().toString().substring(0, 8);
        user.setUserPw(passwordEncoder.encode(tempPassword));
        userRepository.save(user);

        log.info("🔐 임시 비밀번호: {}", tempPassword);

        return tempPassword;
    }
}