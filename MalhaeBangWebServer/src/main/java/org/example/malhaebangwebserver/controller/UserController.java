package org.example.malhaebangwebserver.controller;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.example.malhaebangwebserver.model.entity.Liked;
import org.example.malhaebangwebserver.model.entity.User;
import org.example.malhaebangwebserver.repository.LikedRepository;
import org.example.malhaebangwebserver.security.CustomUserDetails;
import org.example.malhaebangwebserver.service.EmailService;
import org.example.malhaebangwebserver.service.UserService;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Slf4j
@Controller
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;
    private final LikedRepository likedRepository;
    private final EmailService emailService;

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

        try {
            userService.register(email, nickname, password);
        } catch (IllegalArgumentException e) {
            model.addAttribute("error", e.getMessage());
            return "signup";
        }

        return "redirect:/";
    }

    @GetMapping("/mypage")
    public String mypage(Model model, @AuthenticationPrincipal CustomUserDetails userDetails) {
        String email = userDetails.getUsername();
        User user = userService.findByEmail(email);
        List<Liked> likedFolder = likedRepository.findAllByUser_UserId(user.getUserId());
        model.addAttribute("user", user);
        model.addAttribute("likedFolder", likedFolder);

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
            String tempPassword = userService.resetPassword(email);

            // HTML 템플릿 기반 이메일 전송
            emailService.sendTempPasswordHtml(email, tempPassword);

            model.addAttribute("message", "입력하신 이메일로 임시 비밀번호가 발송되었습니다.");
        } catch (IllegalArgumentException e) {
            model.addAttribute("error", "해당 이메일로 등록된 사용자가 없습니다.");
        }

        return "account/findpassword";
    }
}