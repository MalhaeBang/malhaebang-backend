package org.example.malhaebangwebserver.controller;

import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.example.malhaebangwebserver.model.entity.LikedFolder;
import org.example.malhaebangwebserver.model.entity.User;
import org.example.malhaebangwebserver.repository.LikedFolderRepository;
import org.example.malhaebangwebserver.repository.UserRepository;
import org.example.malhaebangwebserver.security.CustomUserDetails;
import org.example.malhaebangwebserver.service.EmailService;
import org.example.malhaebangwebserver.service.UserService;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

@Slf4j
@Controller
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;
    private final EmailService emailService;
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final LikedFolderRepository likedFolderRepository;

     private static final Map<String, String> tempVerificationCodes = new HashMap<>();
    private static final Set<String> verifiedEmails = new HashSet<>();

    @PostMapping("/signup")
    public String signup(
            @RequestParam("id") String email,
            @RequestParam("name") String nickname,
            @RequestParam("password") String password,
            @RequestParam("passwordConfirm") String passwordConfirm,
            Model model
    ) {
        log.info("🔥🔥🔥 [UserController] POST /signup 호출됨");
        if (!password.equals(passwordConfirm)) {
            model.addAttribute("error", "비밀번호가 일치하지 않습니다.");
            return "signup";
        }

        // 이메일 인증 여부 확인
        if (!verifiedEmails.contains(email)) {
            model.addAttribute("error", "이메일 인증을 먼저 완료해주세요.");
            return "signup";
        }

        try {
            userService.register(email, nickname, password);
            
            // 인증된 이메일이므로 바로 verified 상태로 설정
            User user = userRepository.findByUserEmail(email).orElse(null);
            if (user != null) {
                user.setIsVerified(true);
                userRepository.save(user);
            }
            
            // 인증 완료된 이메일 목록에서 제거
            verifiedEmails.remove(email);
            
            model.addAttribute("success", true);
            model.addAttribute("message", "회원가입이 완료되었습니다! 이제 로그인하실 수 있습니다.");
        } catch (IllegalArgumentException e) {
            model.addAttribute("error", e.getMessage());
            return "signup";
        }

        return "account/signup";
    }

    // UserController.java
    @GetMapping("/mypage")
    public String mypage(Model model, @AuthenticationPrincipal CustomUserDetails userDetails) {
        User user = userService.findByEmail(userDetails.getUsername());
        List<LikedFolder> likedFolders = likedFolderRepository.findAllByUser(user);

        model.addAttribute("user", user);
        model.addAttribute("likedFolders", likedFolders); // ✔️ 폴더 단위로 넘김
        return "bootstrap/mypage";
    }

    @PostMapping("/findid")
    public String checkEmailRegistered(@RequestParam("email") String email, Model model) {
        boolean exists = userService.existsByEmail(email);

        if (exists) {

            model.addAttribute("emailFound", true);
            model.addAttribute("email", email);
        } else {
            model.addAttribute("emailFound", false);
        }

        return "account/findid";
    }


    @PostMapping("/findpassword")
    public String findPassword(@RequestParam("email") String email, Model model) {
        try {
            // 1. 사용자 존재 확인
            User user = userRepository.findByUserEmail(email)
                    .orElseThrow(() -> new IllegalArgumentException("해당 이메일로 등록된 사용자가 없습니다."));

            // 2. login_type 확인
            if (user.getLoginType() != org.example.malhaebangwebserver.model.enums.LoginType.FORM) {
                // 소셜 로그인 사용자인 경우
                String socialType = user.getLoginType().name().toLowerCase();
                model.addAttribute("socialError", true);
                model.addAttribute("socialType", socialType);
                return "account/findpassword";
            }

            // 3. 폼 로그인 사용자만 임시 비밀번호 발송
            String tempPassword = userService.resetPassword(email);
            emailService.sendTempPasswordHtml(email, tempPassword);

            model.addAttribute("message", "입력하신 이메일로 임시 비밀번호가 발송되었습니다.");
        } catch (IllegalArgumentException e) {
            model.addAttribute("error", e.getMessage());
        }

        return "account/findpassword";
    }

    // AJAX용 API - 사용자 login_type 확인
    @PostMapping("/check-user-login-type")
    @ResponseBody
    public Map<String, Object> checkUserLoginType(@RequestBody Map<String, String> request) {
        String email = request.get("email");
        Map<String, Object> response = new HashMap<>();
        
        try {
            User user = userRepository.findByUserEmail(email).orElse(null);
            
            if (user == null) {
                response.put("exists", false);
                response.put("loginType", null);
            } else {
                response.put("exists", true);
                response.put("loginType", user.getLoginType().name().toLowerCase());
            }
        } catch (Exception e) {
            response.put("exists", false);
            response.put("loginType", null);
        }
        
        return response;
    }

    // AJAX용 API - 임시 비밀번호 발송
    @PostMapping("/send-temp-password")
    @ResponseBody
    public ResponseEntity<String> sendTempPassword(@RequestBody Map<String, String> request) {
        String email = request.get("email");
        
        try {
            // 사용자 확인 및 login_type 체크
            User user = userRepository.findByUserEmail(email)
                    .orElseThrow(() -> new IllegalArgumentException("사용자를 찾을 수 없습니다."));
                    
            if (user.getLoginType() != org.example.malhaebangwebserver.model.enums.LoginType.FORM) {
                return ResponseEntity.badRequest().body("소셜 로그인 사용자입니다.");
            }
            
            // 임시 비밀번호 발송
            String tempPassword = userService.resetPassword(email);
            emailService.sendTempPasswordHtml(email, tempPassword);
            
            return ResponseEntity.ok("임시 비밀번호가 발송되었습니다.");
        } catch (Exception e) {
            return ResponseEntity.badRequest().body("임시 비밀번호 발송에 실패했습니다.");
        }
    }

    @GetMapping("/changepassword")
    public String changePasswordForm() {
        return "account/changepassword";
    }

    @PostMapping("/changepassword")
    public String changePassword(@AuthenticationPrincipal UserDetails userDetails,
                                 @RequestParam String currentPassword,
                                 @RequestParam String newPassword,
                                 RedirectAttributes redirectAttributes) {

        User user = userRepository.findByUserEmail(userDetails.getUsername())
                .orElseThrow(() -> new UsernameNotFoundException("사용자를 찾을 수 없습니다."));

        if (!passwordEncoder.matches(currentPassword, user.getUserPw())) {
            redirectAttributes.addFlashAttribute("error", "현재 비밀번호가 일치하지 않습니다.");
            return "redirect:/changepassword";
        }

        user.setUserPw(passwordEncoder.encode(newPassword));
        userRepository.save(user);

        redirectAttributes.addFlashAttribute("success", "비밀번호가 성공적으로 변경되었습니다.");
        return "redirect:/mypage";  // 마이페이지로 이동
    }


    @PostMapping("/user/delete")
    public String deleteUser(@AuthenticationPrincipal CustomUserDetails userDetails,
                             HttpServletRequest request,
                             RedirectAttributes redirectAttributes) {
        User user = userDetails.getUser();
        userService.deleteUser(user);

        // 세션 종료 (로그아웃 효과)
        request.getSession().invalidate();

        redirectAttributes.addFlashAttribute("message", "회원 탈퇴가 완료되었습니다.");
        return "redirect:/login?deleted";
    }

    // 이메일 인증번호 요청 (회원가입 전)
    @PostMapping("/verify-email")
    @ResponseBody
    public ResponseEntity<String> sendVerificationCode(@RequestBody Map<String, String> request) {
        String email = request.get("email");
        
        try {
            // 이미 가입된 이메일인지 확인
            if (userService.existsByEmail(email)) {
                return ResponseEntity.badRequest().body("이미 가입된 이메일입니다.");
            }
            
            // 6자리 인증번호 생성 (임시 저장소에 저장)
            String verificationCode = String.format("%06d", (int)(Math.random() * 1000000));
            
            // 로그 출력 (실제로는 Redis나 캐시에 저장해야 함)
            log.info("[인증번호 발송] 이메일: {}, 코드: {}", email, verificationCode);
            
            // 임시로 static 변수에 저장 (실제로는 Redis 사용 권장)
            tempVerificationCodes.put(email, verificationCode);
            
            emailService.sendVerificationCode(email, verificationCode);
            
            return ResponseEntity.ok("인증번호가 발송되었습니다.");
        } catch (Exception e) {
            log.error("[인증번호 발송 실패] 이메일: {}, 오류: {}", email, e.getMessage());
            return ResponseEntity.badRequest().body("인증번호 발송에 실패했습니다.");
        }
    }

    // 인증번호 확인 (회원가입 전)
    @PostMapping("/verify-code")
    @ResponseBody
    public ResponseEntity<String> verifyCode(@RequestBody Map<String, String> request) {
        String email = request.get("email");
        String code = request.get("code");
        
        try {
            String storedCode = tempVerificationCodes.get(email);
            
            if (storedCode != null && storedCode.equals(code)) {
                // 인증 성공
                verifiedEmails.add(email);
                tempVerificationCodes.remove(email); // 사용된 코드 삭제
                
                log.info("✅ [이메일 인증 성공] 이메일: {}", email);
                return ResponseEntity.ok("이메일 인증이 완료되었습니다!");
            } else {
                return ResponseEntity.badRequest().body("인증번호가 일치하지 않습니다.");
            }
        } catch (Exception e) {
            log.error("❌ [인증 실패] 이메일: {}, 오류: {}", email, e.getMessage());
            return ResponseEntity.badRequest().body("인증에 실패했습니다.");
        }
    }
}