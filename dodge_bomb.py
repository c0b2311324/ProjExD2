import math
import os
import random
import sys
import time
import pygame as pg

WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, +5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (+5, 0),
}

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数：こうかとん，または，爆弾のRect
    戻り値：真理値タプル（横判定結果，縦判定結果）
    画面内ならTrue，画面外ならFalse
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate

def game_over(screen, kk_img):
    """
    ゲームオーバー時の処理
    画面をブラックアウトして、泣いているこうかとんの画像と
    「Game Over」の文字列を5秒間表示する
    """
    font = pg.font.Font(None, 80)
    txt = font.render("Game Over", True, (255, 0, 0))
    screen.fill((0, 0, 0))  # 画面を黒で塗りつぶす
    # 泣いているこうかとん画像
    kk_img_gameover = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.9)
    kk_rct_gameover = kk_img_gameover.get_rect()
    kk_rct_gameover2 = kk_img_gameover.get_rect()
    kk_rct_gameover.center = WIDTH//2 - kk_img.get_width()//2-200, HEIGHT//2 - kk_img.get_height()//2+30
    kk_rct_gameover2.center =WIDTH//2 - kk_img.get_width()//2+200, HEIGHT//2 - kk_img.get_height()//2+30
    screen.blit(kk_img_gameover, kk_rct_gameover)
    screen.blit(kk_img_gameover, kk_rct_gameover2)
    screen.blit(txt, [WIDTH//2-170, HEIGHT//2])
    pg.display.update()
    time.sleep(5)  # 5秒間表示

def create_bomb_surfaces_and_accelerations() -> tuple[list[pg.Surface], list[int]]:
    """
    10段階の拡大された爆弾Surfaceと加速度のリストを生成して返す。
    
    戻り値:
        tuple[list[pg.Surface], list[int]]: 爆弾のSurfaceリストと加速度リスト
    """
    bb_imgs = []
    bb_accs = [a for a in range(1, 11)]  # 加速度リスト

    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r), pg.SRCALPHA)  # 拡大された爆弾のSurface
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)  # 爆弾を描画
        bb_imgs.append(bb_img)

    return bb_imgs, bb_accs #爆弾の大きさと、加速度の速さを返す

def calculate_velocity(kk_rct: pg.Rect, bb_rct: pg.Rect) -> tuple[float, float]:
    """
    こうかとんに追従する爆弾の速度ベクトルを計算する。
    
    引数:
        kk_rct (pg.Rect): こうかとんのRect
        bb_rct (pg.Rect): 爆弾のRect

    戻り値:
        tuple[float, float]: 正規化された速度ベクトル
    """
    # 差ベクトル（こうかとんから見た爆弾の位置）
    diff_x = kk_rct.centerx - bb_rct.centerx
    diff_y = kk_rct.centery - bb_rct.centery
    
    # 距離（差ベクトルのノルム）
    distance = math.sqrt(diff_x**2 + diff_y**2)

    # 正規化された速度ベクトル
    if distance != 0:
        norm = 5  # 速度の大きさを5に設定
        new_vx = (diff_x / distance) * norm
        new_vy = (diff_y / distance) * norm
    else:
        new_vx, new_vy = 0, 0

    return new_vx, new_vy

def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    # 爆弾のSurfaceと加速度を準備
    bb_imgs, bb_accs = create_bomb_surfaces_and_accelerations()

    # 爆弾の初期設定
    bb_rct = bb_imgs[0].get_rect()  # 最初の爆弾のRectを取得
    bb_rct.centerx = random.randint(0, WIDTH)
    bb_rct.centery = random.randint(0, HEIGHT)

    clock = pg.time.Clock()
    tmr = 0

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return

        screen.blit(bg_img, [0, 0])

        # こうかとんの操作
        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]  # 横座標, 縦座標
        for key, tpl in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += tpl[0]  # 横方向
                sum_mv[1] += tpl[1]  # 縦方向
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
        screen.blit(kk_img, kk_rct)

        # 爆弾の拡大と加速度の適用
        step = min(tmr // 500, 9)  # 500フレームごとにステップを進め、最大9
        bb_img = bb_imgs[step]  # 適切な大きさの爆弾Surfaceを選択
        bb_rct = bb_img.get_rect(center=bb_rct.center)  # 爆弾の中心位置を維持

        # 爆弾の追従移動
        avx, avy = calculate_velocity(kk_rct, bb_rct)
        bb_rct.move_ip(avx, avy)
        screen.blit(bb_img, bb_rct)

        # 爆弾がこうかとんに衝突したらゲームオーバー処理
        if kk_rct.colliderect(bb_rct):
            game_over(screen, kk_img)
            return

        pg.display.update()
        tmr += 1
        clock.tick(50)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()

