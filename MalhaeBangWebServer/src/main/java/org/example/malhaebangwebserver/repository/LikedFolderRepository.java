package org.example.malhaebangwebserver.repository;

import org.example.malhaebangwebserver.model.entity.LikedFolder;
import org.example.malhaebangwebserver.model.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface LikedFolderRepository extends JpaRepository<LikedFolder, Integer> {
    List<LikedFolder> findAllByUser(User user);

}
