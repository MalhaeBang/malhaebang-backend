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
        return new CustomUserDetails(user);
    }
}