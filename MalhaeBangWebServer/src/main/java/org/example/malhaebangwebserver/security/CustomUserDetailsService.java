package org.example.malhaebangwebserver.security;

import lombok.RequiredArgsConstructor;
import org.example.malhaebangwebserver.model.entity.User;
import org.example.malhaebangwebserver.repository.UserRepository;
import org.springframework.security.core.userdetails.*;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class CustomUserDetailsService implements UserDetailsService {
    private final UserRepository userRepository;

    @Override
    public UserDetails loadUserByUsername(String email) throws UsernameNotFoundException {
        User user = userRepository.findByUserEmail(email)
                .orElseThrow(() -> new UsernameNotFoundException("해당 이메일이 존재하지 않습니다."));
        
        // 이메일 인증이 완료되지 않은 사용자는 로그인 불가 (소셜 로그인 제외)
        if (user.getLoginType() == org.example.malhaebangwebserver.model.enums.LoginType.FORM && !user.getIsVerified()) {
            throw new UsernameNotFoundException("이메일 인증이 완료되지 않았습니다. 이메일을 확인해주세요.");
        }
        
        return new CustomUserDetails(user);
    }
}