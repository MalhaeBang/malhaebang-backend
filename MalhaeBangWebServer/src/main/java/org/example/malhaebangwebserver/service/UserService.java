package org.example.malhaebangwebserver.service;

import org.example.malhaebangwebserver.model.dto.UserDto;
import org.example.malhaebangwebserver.model.entity.User;
import org.example.malhaebangwebserver.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

@Service
public class UserService {

    @Autowired
    private UserRepository userRepository;

    public List<UserDto> getAllUsers() {
        return userRepository.findAll().stream()
                .map(user -> UserDto.builder()
                        .id(user.getId())
                        .name(user.getName())
                        .email(user.getEmail())
                        .build())
                .collect(Collectors.toList());
    }

    public UserDto createUser(UserDto dto) {
        User user = User.builder()
                .name(dto.getName())
                .email(dto.getEmail())
                .build();

        User saved = userRepository.save(user);

        return UserDto.builder()
                .id(saved.getId())
                .name(saved.getName())
                .email(saved.getEmail())
                .build();
    }

    public UserDto getUserById(Long id) {
        User user = userRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("User not found with id " + id));

        return UserDto.builder()
                .id(user.getId())
                .name(user.getName())
                .email(user.getEmail())
                .build();
    }

    public UserDto updateUser(Long id, UserDto dto) {
        User user = userRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("User not found with id " + id));

        user.setName(dto.getName());
        user.setEmail(dto.getEmail());

        User updated = userRepository.save(user);

        return UserDto.builder()
                .id(updated.getId())
                .name(updated.getName())
                .email(updated.getEmail())
                .build();
    }

    public void deleteUser(Long id) {
        userRepository.deleteById(id);
    }
}