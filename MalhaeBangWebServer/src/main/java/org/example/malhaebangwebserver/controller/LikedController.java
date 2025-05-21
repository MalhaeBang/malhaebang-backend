package org.example.malhaebangwebserver.controller;

import lombok.RequiredArgsConstructor;
import org.example.malhaebangwebserver.model.dto.LikedFolderDto;
import org.example.malhaebangwebserver.model.entity.*;
import org.example.malhaebangwebserver.repository.*;
import org.example.malhaebangwebserver.security.CustomUserDetails;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import lombok.extern.slf4j.Slf4j;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.Optional;


@Slf4j
@RestController
@RequiredArgsConstructor
@RequestMapping("/api/like")
public class LikedController {

    private final LikedRepository likedRepository;
    private final HouseRepository houseRepository;
    private final LikedFolderRepository likedFolderRepository;

    @PostMapping("/{houseId}")
    public ResponseEntity<String> toggleLike(
            @PathVariable Integer houseId,
            @AuthenticationPrincipal CustomUserDetails userDetails
    ) {
        User user = userDetails.getUser();

        Optional<House> houseOpt = houseRepository.findById(houseId);
        if (houseOpt.isEmpty()) {

            return ResponseEntity.badRequest().body("해당 매물을 찾을 수 없습니다.");
        }

        House house = houseOpt.get();

        // 기본 찜 폴더 확인 또는 생성
        LikedFolder folder = likedFolderRepository.findAllByUser(user).stream()
                .findFirst()
                .orElseGet(() -> {
                    LikedFolder newFolder = LikedFolder.builder()
                            .user(user)
                            .folderName("기본 폴더")
                            .createdAt(LocalDateTime.now())
                            .build();
                    return likedFolderRepository.save(newFolder);
                });

        // 이미 찜한 경우 -> 삭제
        Optional<Liked> existingLike = likedRepository.findByUserAndHouse(user, house);
        if (existingLike.isPresent()) {
            likedRepository.delete(existingLike.get());
            return ResponseEntity.ok("찜 해제됨");
        }

        // 새 찜 추가
        Liked liked = Liked.builder()
                .user(user)
                .house(house)
                .likedAt(LocalDateTime.now())
                .isLiked(true)
                .folder(folder)
                .build();
        likedRepository.save(liked);
        return ResponseEntity.ok("찜 추가됨");
    }


    @PostMapping("/{houseId}/folder/{folderId}")
    public ResponseEntity<String> likeToFolder(
            @PathVariable Integer houseId,
            @PathVariable Integer folderId,
            @AuthenticationPrincipal CustomUserDetails userDetails) {

        User user = userDetails.getUser();

        Optional<House> houseOpt = houseRepository.findById(houseId);
        Optional<LikedFolder> folderOpt = likedFolderRepository.findById(folderId);

        if (houseOpt.isEmpty()) {
            return ResponseEntity.badRequest().body("❌ 해당 매물을 찾을 수 없습니다.");
        }

        if (folderOpt.isEmpty() || !folderOpt.get().getUser().getUserId().equals(user.getUserId())) {
            return ResponseEntity.badRequest().body("❌ 폴더가 없거나 권한이 없습니다.");
        }

        House house = houseOpt.get();
        LikedFolder folder = folderOpt.get();

        Optional<Liked> existingLike = likedRepository.findByUserAndHouse(user, house);
        if (existingLike.isPresent()) {
            return ResponseEntity.ok("⚠ 이미 찜한 매물입니다.");
        }

        Liked liked = Liked.builder()
                .user(user)
                .house(house)
                .folder(folder)
                .likedAt(LocalDateTime.now())
                .isLiked(true)
                .build();
        likedRepository.save(liked);

        return ResponseEntity.ok("✅ 찜이 폴더에 추가되었습니다.");
    }

    @GetMapping("/folders")
    public ResponseEntity<?> getUserFolders(@AuthenticationPrincipal CustomUserDetails userDetails) {
        User user = userDetails.getUser();
        List<LikedFolder> folders = likedFolderRepository.findAllByUser(user);

        // 🔍 로그 확인
        log.info("📦 로그인한 유저 ID: {}", user.getUserId());
        log.info("📦 해당 유저 폴더 개수: {}", folders.size());
        folders.forEach(f -> log.info("📦 폴더명: {}, 폴더 ID: {}", f.getFolderName(), f.getFolderId()));

        // ✅ DTO로 변환 후 반환
        List<LikedFolderDto> response = folders.stream()
                .map(f -> new LikedFolderDto(f.getFolderId(), f.getFolderName()))
                .toList();

        return ResponseEntity.ok(response);
    }

    @PostMapping("/folder")
    public ResponseEntity<String> createFolder(
            @RequestBody Map<String, String> body,
            @AuthenticationPrincipal CustomUserDetails userDetails) {

        String folderName = body.get("folderName");
        if (folderName == null || folderName.trim().isEmpty()) {
            return ResponseEntity.badRequest().body("폴더 이름이 비어있습니다.");
        }

        LikedFolder folder = LikedFolder.builder()
                .folderName(folderName.trim())
                .createdAt(LocalDateTime.now())
                .user(userDetails.getUser())
                .build();
        likedFolderRepository.save(folder);
        return ResponseEntity.ok("폴더가 생성되었습니다.");
    }
}