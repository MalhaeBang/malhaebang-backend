package org.example.malhaebangwebserver.service;

import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.example.malhaebangwebserver.model.entity.LikedFolder;
import org.example.malhaebangwebserver.model.entity.User;
import org.example.malhaebangwebserver.model.enums.LoginType;
import org.example.malhaebangwebserver.repository.LikedFolderRepository;
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
    private final LikedFolderRepository likedFolderRepository;

    @Transactional
    public void register(String email, String nickname, String password) {
        log.info("[회원가입 시도] 이메일: {}", email);
        if (userRepository.existsByUserEmail(email)) {
            throw new IllegalArgumentException("이미 존재하는 이메일입니다.");
        }

        // 인증 토큰 생성
        String verificationToken = UUID.randomUUID().toString();

        User user = User.builder()
                .userEmail(email)
                .userPw(passwordEncoder.encode(password))
                .userNickname(nickname)
                .createdAt(LocalDateTime.now())
                .isDeleted(false)
                .loginType(LoginType.FORM)
                .verificationToken(verificationToken)
                .isVerified(false) // 이메일 인증 전까지는 비활성화
                .build();

        log.info("[회원 생성 직전]");
        User savedUser = userRepository.save(user);
        log.info("[회원 생성 완료]");
        
        LikedFolder defaultFolder = LikedFolder.builder()
                .user(savedUser)
                .folderName("기본 폴더")
                .createdAt(LocalDateTime.now())
                .build();
        likedFolderRepository.save(defaultFolder);

        log.info("[인증 이메일 발송 중] 토큰: {}", verificationToken);
        // 여기서는 EmailService 주입이 필요하므로 별도 메서드로 분리
    }

    @Transactional
    public String createVerificationCode(String email) {
        // 6자리 랜덤 숫자 생성
        String verificationCode = String.format("%06d", (int)(Math.random() * 1000000));
        
        User user = userRepository.findByUserEmail(email)
                .orElseThrow(() -> new IllegalArgumentException("사용자를 찾을 수 없습니다."));
        
        user.setVerificationToken(verificationCode); // 토큰 필드에 6자리 코드 저장
        userRepository.save(user);
        
        return verificationCode;
    }

    @Transactional
    public boolean verifyEmailWithCode(String email, String code) {
        User user = userRepository.findByUserEmail(email).orElse(null);
        
        if (user != null && user.getVerificationToken() != null && user.getVerificationToken().equals(code)) {
            user.setIsVerified(true);
            user.setVerificationToken(null); // 코드 사용 후 삭제
            userRepository.save(user);
            log.info("[이메일 인증 완료] 사용자: {}", user.getUserEmail());
            return true;
        }
        
        log.warn("[이메일 인증 실패] 이메일: {}, 입력 코드: {}", email, code);
        return false;
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

        log.info("임시 비밀번호: {}", tempPassword);

        return tempPassword;
    }
    @Transactional
    public void deleteUser(User user) {
        user.setIsDeleted(true);
        userRepository.save(user);
        log.info("회원 탈퇴 처리 완료: {}", user.getUserEmail());
    }
}