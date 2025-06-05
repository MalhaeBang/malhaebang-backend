package org.example.malhaebangwebserver.service;

import jakarta.mail.MessagingException;
import jakarta.mail.internet.MimeMessage;
import lombok.RequiredArgsConstructor;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;
import org.springframework.stereotype.Service;
import org.thymeleaf.TemplateEngine;
import org.thymeleaf.context.Context;

@Service
@RequiredArgsConstructor
public class EmailService {

    private final JavaMailSender mailSender;
    private final TemplateEngine templateEngine;

    public void sendTempPasswordHtml(String toEmail, String tempPassword) {
        Context context = new Context();
        context.setVariable("tempPassword", tempPassword);

        String htmlContent = templateEngine.process("mail/temp-password", context); // templates/mail/temp-password.html

        try {
            MimeMessage message = mailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(message, true, "UTF-8");

            helper.setTo(toEmail);
            helper.setSubject("[MalhaeBang] 임시 비밀번호 안내");
            helper.setText(htmlContent, true);

            mailSender.send(message);
        } catch (MessagingException e) {
            throw new RuntimeException("메일 전송 실패", e);
        }
    }

    public void sendVerificationCode(String toEmail, String verificationCode) {
        try {
            MimeMessage message = mailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(message, true, "UTF-8");

            helper.setTo(toEmail);
            helper.setSubject("[MalhaeBang] 이메일 인증번호");
            
            String htmlContent = String.format(
                "<div style='font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px;'>" +
                "<h2 style='color: #4d68ff;'>MalhaeBang 이메일 인증</h2>" +
                "<p>안녕하세요! 아래 인증번호를 입력하여 이메일 인증을 완료해주세요.</p>" +
                "<div style='background: #f8f9fc; padding: 20px; text-align: center; margin: 20px 0;'>" +
                "<h1 style='color: #4d68ff; font-size: 32px; letter-spacing: 5px; margin: 0;'>%s</h1>" +
                "</div>" +
                "<p style='color: #666;'>인증번호는 10분간 유효합니다.</p>" +
                "<p style='color: #666;'>감사합니다.</p>" +
                "</div>", 
                verificationCode
            );
            
            helper.setText(htmlContent, true);
            mailSender.send(message);
            
        } catch (MessagingException e) {
            throw new RuntimeException("인증번호 전송 실패", e);
        }
    }

}